# encoding: utf-8
import os
import base64
from typing import Any
#from suds import WebFault
from zeep import Client
#from suds.client import Client
from lxml import etree as ET
import logging

#import xmltodict

from .exceptions import WSClientException, WSExistingCfdiException

class Cliente:
  
  response: Any
    
  def __init__(self, url, opciones = {}, debug = False):
    self.debug = debug
    self.url = url
    self.opciones = {}
    if self.debug: self._activa_debug()

    for key, value in opciones.items():
      if key in ['Contrato', 'UserID', 'UserPass']:
        self.opciones.update({ key: value })

  def timbrar(self, src, opciones = { 'generarCBB': False, 'generarTXT': False, 'generarPDF': False}):
    #try:
      # en caso de que src sea una ruta a archivo y no una cadena, abrir y cargar ruta
      #if os.path.isfile(src): src = open(src, 'rb').read()
      
      #opciones['text2CFDI'] = base64.b64encode(src)
      #print(base64.b64encode(src))
           
      
      #self.opciones.update(opciones)
      cliente = Client(self.url)
      print("llego hasta aca_timbrar")

      
      #respuesta = cliente.service.EmitirTimbrar("EWE1709045U0.Test", "Prueba$1", 192919990, str(base64.b64encode(src),"utf-8"))
      #print(self.opciones)
      #xml_cfdi = str(src.xml_bytes().decode("UTF-8"))
      xml_cfdi = src.xml_bytes()
      print("xml")
      print(xml_cfdi)
      #respuesta = cliente.service.EmitirTimbrar(self.opciones['UserID'], self.opciones['UserPass'], self.opciones['Contrato'], str(base64.b64encode(src),"UTF-8"))
      self.response = cliente.service.EmitirTimbrar(self.opciones['UserID'], self.opciones['UserPass'], self.opciones['Contrato'], str(base64.b64encode(xml_cfdi),"UTF-8"))
      #respuesta = cliente.service.EmitirTimbrar(self.opciones['UserID'], self.opciones['UserPass'], self.opciones['Contrato'], xml_cfdi)
      print(self.response)
      #self.response.data = respuesta['XML']
      #self.response.message = respuesta['message']
      print("respuesta recibida")
      self.raise_from_code()
      #print("respuesta",respuesta)
     

        
      #return True
      #return respuesta['XML'],  respuesta['message'],
      return self.response.XML, self.response.message
    

   # except WebFault as e:
   #   self.__dict__['codigo_error'] = e.fault.faultcode
   #   self.__dict__['error'] = e.fault.faultstring
   #   self.__dict__['message'] = e.fault.faultstring #self.__response
   #   if self.debug:
   #     self.logger.error("\nSOAP request:\n %s\nSOAP response: [%s] - %s" % (cliente.last_sent(), e.fault.faultcode, e.fault.faultstring))
   #   return False
   # except Exception as e:
   #   self.__dict__['codigo_error'] = 'Error desconocido'
   #   self.__dict__['error'] = e
   #   self.__dict__['message'] = e.fault.faultstring #self.__response
  # except
      
   
      #return False
  def raise_from_code(self):
        """Raises a WSClientException if the given code is not 200.

        Raises:
            WSClientException: If the given code is not 200.
            WSExistingCfdiException: If the given code is 307.
        """
        res = self.response
        if res.isError == True:
          match res.codigoError:
              case "200" | "201":
                  return
              case "24":
                #self.logger.info({"code": res.codigoError, "message": res.message})
                  raise WSExistingCfdiException(res.message, res.codigoError, res.XML)
              case _:
                #self.logger.info({"code": res.codigoError, "message": res.message})
                  raise WSClientException(res.message, res.codigoError)

  def cancelar(self, uuid):
    try:
      cliente = Client(self.url)
      opciones = {'uuid': uuid}
      opciones.update(self.opciones)
      respuesta = cliente.service.requestCancelarCFDI(opciones)
      if self.debug:
        self.logger.info("\nSOAP request:\n %s" % cliente.last_sent())
        self.logger.info("\nSOAP response:\n %s" % cliente.last_received())
      return True
    except WebFault as e:
      self.__dict__['codigo_error'] = e.fault.faultcode
      self.__dict__['error'] = e.fault.faultstring
      if self.debug:
        self.logger.error("\nSOAP request:\n %s\nSOAP response: [%s] - %s" % (cliente.last_sent(), e.fault.faultcode, e.fault.faultstring))
      return False
    except Exception as e:
      self.__dict__['codigo_error'] = 'Error desconocido'
      self.__dict__['error'] = e.message
      return False

  def activarCancelacion(self, archCer, archKey, passKey):
    try:
      # en caso de que archCer y/o archKey sean una ruta a archivo y no una cadena, abrir y cargar ruta
      if os.path.isfile(archCer): archCer = open(archCer, 'r').read()
      if os.path.isfile(archKey): archKey = open(archKey, 'r').read()
      opciones = {}
      opciones['archivoKey'] = base64.b64encode(archKey)
      opciones['archivoCer'] = base64.b64encode(archCer)
      opciones['clave'] = passKey
      self.opciones.update(opciones)
      cliente = Client(self.url)
      respuesta = cliente.service.activarCancelacion(self.opciones)
      if self.debug:
        self.logger.info("\nSOAP request:\n %s" % cliente.last_sent())
        self.logger.info("\nSOAP response:\n %s" % cliente.last_received())
      return True
    except WebFault as e:
      self.__dict__['codigo_error'] = e.fault.faultcode
      self.__dict__['error'] = e.fault.faultstring
      if self.debug:
        self.logger.error("\nSOAP request:\n %s\nSOAP response: [%s] - %s" % (cliente.last_sent(), e.fault.faultcode, e.fault.faultstring))
      return False
    except Exception as e:
      self.__dict__['codigo_error'] = 'Error desconocido'
      self.__dict__['error'] = e.message
      return False

  def _activa_debug(self):
    if not os.path.exists('log'): os.makedirs('log')
    self.logger = logging.getLogger('facturacion_moderna')
    hdlr = logging.FileHandler('log/facturacion_moderna.log')
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    self.logger.addHandler(hdlr) 
    self.logger.setLevel(logging.INFO)
      
