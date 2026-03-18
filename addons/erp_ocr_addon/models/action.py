# -*- coding: utf-8 -*-
import base64
import logging

from odoo import models, _
from odoo.exceptions import UserError

from .azure import AzureInvoiceService

_logger = logging.getLogger(__name__)


class OCRDocumentAction(models.Model):
    _inherit = "ocr.document"

    def action_run_ocr(self):
        """
        Manual OCR trigger from button.
        Uses AzureInvoiceService defined in azure.py
        """
        self.ensure_one()

        if not self.file:
            raise UserError(_("Please upload a document first."))

        if self.status == "processing":
            raise UserError(_("OCR is already running."))

        _logger.info("Starting OCR from action for document %s", self.name)

        self.write({
            "status": "processing",
            "progress": 10.0,
            "ocr_error_message": False,
        })

        try:
            # Initialize Azure OCR service
            service = AzureInvoiceService(self.env)

            # Run OCR
            raw_data = service.analyze(base64.b64decode(self.file))

            if not raw_data:
                raise UserError(_("No data returned from Azure OCR."))

            # Delegate processing to document logic
            self._process_ocr_result(raw_data)

            self.write({
                "status": "done",
                "progress": 100.0,
            })

            _logger.info("OCR completed successfully for document %s", self.name)

        except UserError:
            raise

        except Exception as e:
            _logger.exception("OCR action failed")

            self.write({
                "status": "failed",
                "progress": 0.0,
                "ocr_error_message": str(e),
            })

            raise UserError(_("OCR processing failed. Please check logs."))