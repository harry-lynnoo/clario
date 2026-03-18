# -*- coding: utf-8 -*-
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest

from odoo.exceptions import UserError

import logging
import re

_logger = logging.getLogger(__name__)


class AzureInvoiceService:
    """
    Structured Azure-first extraction layer.

    IMPORTANT:
    - Reads Azure configuration from Odoo Settings
    - Works with Azure Document Intelligence
    """

    def __init__(self, env):
        config = env["ir.config_parameter"].sudo()

        endpoint = config.get_param("clario_ocr.azure_endpoint")
        key = config.get_param("clario_ocr.azure_api_key")

        if not endpoint or not key:
            raise UserError(
                "Azure OCR is not configured.\n\n"
                "Go to Settings → Clario OCR → Azure Configuration."
            )

        self.client = DocumentIntelligenceClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key),
        )

    # ======================================================
    # NORMALIZATION HELPERS
    # ======================================================

    def _normalize_phone(self, s: str) -> str:
        if not s:
            return ""
        return re.sub(r"[ \t\r\n\-\(\)\.]", "", s.strip())

    def _normalize_website(self, s: str) -> str:
        if not s:
            return ""
        return s.strip().rstrip(".,;:)")

    # ======================================================
    # SAFE FALLBACK EXTRACTORS
    # ======================================================

    def _extract_phone_from_text(self, text: str):
        if not text:
            return None

        pat = r"(?:เบอร์โทร|โทรศัพท์|Tel\.?|Phone)\s*[:\|]?\s*([+0-9][0-9 \-\(\)\.]{7,})"
        m = re.search(pat, text, flags=re.IGNORECASE)

        if m:
            return self._normalize_phone(m.group(1))

        loose = re.findall(r"(\+66[0-9]{8,9}|0[0-9]{8,9})", text)

        return loose[0] if loose else None

    def _extract_vendor_website_from_text(self, text: str):
        if not text:
            return None

        m = re.search(
            r"(Website|เว็บไซต์)\s*[:\-]?\s*(https?://\S+|www\.[^\s]+)",
            text,
            flags=re.IGNORECASE,
        )

        return self._normalize_website(m.group(2)) if m else None

    def _extract_branch_from_text(self, text: str):
        if not text:
            return None

        m = re.search(r"(รหัสสาขา)\s*[:\-]?\s*(\d{4,6})", text)

        if m:
            return f"Branch {m.group(2)}"

        m = re.search(r"(?:Branch)\s*[:\-]?\s*(\d{4,6})", text, flags=re.IGNORECASE)

        if m:
            return f"Branch {m.group(1)}"

        return None

    # ======================================================
    # ADDRESS STRUCTURED HANDLER
    # ======================================================

    def _get_structured_address(self, field):
        if not field or not getattr(field, "value_address", None):
            return None

        addr = field.value_address

        return {
            "house_number": getattr(addr, "house_number", None),
            "road": getattr(addr, "road", None),
            "city": getattr(addr, "city", None),
            "city_district": getattr(addr, "city_district", None),
            "postal_code": getattr(addr, "postal_code", None),
            "country_region": getattr(addr, "country_region", None),
            "street_address": getattr(addr, "street_address", None),
            "unit": getattr(addr, "unit", None),
            "house": getattr(addr, "house", None),
            "raw": getattr(field, "content", None),
        }

    # ======================================================
    # MAIN ANALYSIS
    # ======================================================

    def analyze(self, file_bytes: bytes, doc_type: str = "invoice") -> dict:

        model_id = "prebuilt-receipt" if doc_type == "receipt" else "prebuilt-invoice"

        poller = self.client.begin_analyze_document(
            model_id,
            AnalyzeDocumentRequest(bytes_source=file_bytes),
        )

        result = poller.result()

        raw_text = getattr(result, "content", None) or ""

        if not getattr(result, "documents", None):
            return {"raw_text": raw_text}

        doc = result.documents[0]

        fields = doc.fields or {}

        _logger.info("AZURE FIELD KEYS: %s", list(fields.keys()))

        def fget(name):
            return fields.get(name)

        def get_string(name):
            f = fget(name)
            return f.value_string if f else None

        def get_date(name):
            f = fget(name)
            return f.value_date if f else None

        def get_currency(name):
            f = fget(name)

            if not f or not getattr(f, "value_currency", None):
                return (None, None)

            cur = f.value_currency

            return (cur.amount, getattr(cur, "currency_code", None))

        # ==================================================
        # PARTY FIELDS
        # ==================================================

        if doc_type == "receipt":
            vendor_name = get_string("MerchantName")
        else:
            vendor_name = get_string("VendorAddressRecipient") or get_string("VendorName")

        customer_name = get_string("CustomerAddressRecipient") or get_string("CustomerName")

        vendor_tax_id = get_string("VendorTaxId")

        customer_tax_id = get_string("CustomerTaxId")

        vendor_phone = get_string("VendorPhoneNumber") or self._extract_phone_from_text(raw_text)

        customer_phone = get_string("CustomerPhoneNumber")

        vendor_website = get_string("VendorWebsite") or self._extract_vendor_website_from_text(raw_text)

        if vendor_website:
            vendor_website = self._normalize_website(vendor_website)

        vendor_branch_name = self._extract_branch_from_text(raw_text)

        if doc_type == "receipt":
            vendor_address_struct = self._get_structured_address(fget("MerchantAddress"))
        else:
            vendor_address_struct = self._get_structured_address(fget("VendorAddress"))

        customer_address_struct = self._get_structured_address(fget("CustomerAddress"))

        # ==================================================
        # DOCUMENT INFO
        # ==================================================

        if doc_type == "receipt":

            invoice_id = get_string("ReceiptId")

            reference_number = None

            invoice_date = get_date("TransactionDate")

            due_date = None

            payment_terms = None

        else:

            invoice_id = get_string("InvoiceId")

            reference_number = get_string("PurchaseOrder") or get_string("ReferenceNumber")

            invoice_date = get_date("InvoiceDate")

            due_date = get_date("DueDate")

            payment_terms = get_string("PaymentTerm")

        # ==================================================
        # FINANCIALS
        # ==================================================

        if doc_type == "receipt":

            subtotal, c1 = get_currency("Subtotal")

            discount, c2 = get_currency("Discount")

            vat, c3 = get_currency("TotalTax")

            total, c4 = get_currency("Total")

        else:

            subtotal, c1 = get_currency("SubTotal")

            discount, c2 = get_currency("TotalDiscount")

            vat, c3 = get_currency("TotalTax")

            total, c4 = get_currency("InvoiceTotal")

        currency_code = c4 or c3 or c2 or c1

        # ==================================================
        # ITEMS
        # ==================================================

        items = []

        items_field = fget("Items")

        items_sum_amount = 0.0

        items_sum_unitprice_qty = 0.0

        items_source = "none"

        if items_field and getattr(items_field, "value_array", None):

            items_source = "azure_items"

            for item in items_field.value_array:

                obj = getattr(item, "value_object", None)

                if not obj:
                    continue

                def l_str(k):
                    return obj.get(k).value_string if obj.get(k) else ""

                def l_num(k):
                    return obj.get(k).value_number if obj.get(k) else 0.0

                def l_money(k):
                    return (
                        obj.get(k).value_currency.amount
                        if obj.get(k) and getattr(obj.get(k), "value_currency", None)
                        else 0.0
                    )

                desc = l_str("Description")

                code = l_str("ProductCode")

                qty = l_num("Quantity") or 0.0

                if doc_type == "receipt":
                    unit_price = l_money("Price") or 0.0
                    amt = l_money("TotalPrice") or 0.0
                else:
                    unit_price = l_money("UnitPrice") or 0.0
                    amt = l_money("Amount") or 0.0

                items.append(
                    {
                        "description": desc,
                        "product_code": code,
                        "quantity": qty if qty else 1.0,
                        "unit_price": unit_price,
                        "amount": amt,
                    }
                )

                try:
                    items_sum_amount += float(amt or 0.0)
                except Exception:
                    pass

                try:
                    items_sum_unitprice_qty += float(qty or 0.0) * float(unit_price or 0.0)
                except Exception:
                    pass

        items_sum_amount = round(items_sum_amount, 2)

        items_sum_unitprice_qty = round(items_sum_unitprice_qty, 2)

        confidence = doc.confidence if hasattr(doc, "confidence") else 0.9

        customer_id = get_string("CustomerId")

        return {
            "raw_text": raw_text,
            "confidence_score": confidence,
            "currency_code": currency_code,
            "invoice_id": invoice_id,
            "reference_number": reference_number,
            "invoice_date": invoice_date,
            "due_date": due_date,
            "payment_terms": payment_terms,
            "vendor_name": vendor_name,
            "vendor_branch_name": vendor_branch_name,
            "vendor_tax_id": vendor_tax_id,
            "vendor_phone": vendor_phone,
            "vendor_website": vendor_website,
            "vendor_address_struct": vendor_address_struct,
            "customer_name": customer_name,
            "customer_tax_id": customer_tax_id,
            "customer_id": customer_id,
            "customer_phone": customer_phone,
            "customer_address_struct": customer_address_struct,
            "subtotal_amount": subtotal,
            "discount_amount": discount,
            "vat_amount": vat,
            "total_amount": total,
            "items": items,
            "items_sum_amount": items_sum_amount,
            "items_sum_unitprice_qty": items_sum_unitprice_qty,
            "items_source": items_source,
        }