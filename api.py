import uvicorn
import ssl
from Backend.app import config

if __name__=="__main__":
    if config.settings.RUN_ON_HTTPS:
        uvicorn.run("Backend.app.app:app", 
                    host=config.settings.HOST, 
                    port=config.settings.PORT, 
                    reload=config.settings.DEBUG_MODE,
                    ssl_version=ssl.PROTOCOL_SSLv23,
                    # cert_reqs=ssl.CERT_OPTIONAL,
                    ssl_keyfile=config.settings.BACKEND_SSL_KEY_FILE,        # Manually Generated certificates
                    ssl_certfile=config.settings.BACKEND_SSL_CRT_FILE,      # are used here
                    )     
    else:
        uvicorn.run("Backend.app.app:app", 
                    host=config.settings.HOST, 
                    port=config.settings.PORT, 
                    reload=config.settings.DEBUG_MODE,
                    )     
    #Location is specified as app/test.py and it is the main fastapi file
    #HOST, PORT and DEBUG_MODE can be configured in config.py