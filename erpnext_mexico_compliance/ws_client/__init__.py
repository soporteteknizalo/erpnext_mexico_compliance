"""Copyright (c) 2024, TI Sin Problemas and contributors
For license information, please see license.txt"""

import frappe

from . import client
from .exceptions import WSClientException, WSExistingCfdiException


def get_ws_client(settings=None) -> client.WSClient:
    """Retrieves a WSClient instance based on the current CFDI Stamping Settings.

    Args:
        settings (CFDIStampingSettings, optional): The CFDI Stamping Settings document. Defaults to None.

    Returns:
        client.WSClient: A WSClient instance configured with the current API key and operation mode.
    """
    if not settings:
        settings = frappe.get_single("CFDI Stamping Settings")
    api_key = settings.get_api_key()
    
    
    mode_map = {
        0: client.WSClient.OperationMode.PROD,
        1: client.WSClient.OperationMode.TEST,
    }
    #return client.WSClient(api_key, mode_map[settings.test_mode])
    return client.WSClient(api_key)


__all__ = ["get_ws_client", "WSClientException", "WSExistingCfdiException"]
