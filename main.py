from fastapi import FastAPI
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ed25519
import hashlib
import base64

app = FastAPI()
# HARDCODED PRIVATE KEY - DO NOT USE IN PRODUCTION
PRIVATE_KEY_PEM = b'''-----BEGIN PRIVATE KEY-----
MC4CAQAwBQYDK2VwBCIEIHWtkybETJMS/MnzKkC0te0yMkqNrYCE4GRQxhn5wXyi
-----END PRIVATE KEY-----'''
password = None # Set to None for unencrypted keys

try:
    private_key = serialization.load_pem_private_key(
        PRIVATE_KEY_PEM,
        password=password,
    )
    public_key = serialization.load_pem_public_key(b'''-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAjfR+rANQfjvZjNwThaI9razGeJFPAqDSJxfflxu3s1A=
-----END PUBLIC KEY-----''')
    print("Ed25519 public key imported successfully.")
except ValueError as e:
    print(f"Error importing key: {e}")


class HealthCheck(BaseModel):
    status: str = "ok"

@app.get("/health")
async def health_check() -> HealthCheck:
    """
    Simple health check endpoint that returns 200 OK
    """
    return HealthCheck()

@app.get("/")
async def root():
    return {"message": "Hello World"}



class SignRequest(BaseModel):
    data: str
    status: str

class SignResponse(BaseModel):
    task_id: str
    exp_dt: str
    signature_hex: str
    status: str

@app.post("/sign", response_model=SignResponse)
async def sign_message(request: SignRequest):
    try:
        # print(request.payload)
        # return {"message":"hi encryption"}

        # private_key = serialization.load_pem_private_key(
        #     PRIVATE_KEY_PEM,
        #     password=None
        # )
        
        # signature = private_key.sign(
        #     request.payload.encode('utf-8'),
        #     padding.PKCS1v15(),
        #     hashes.SHA256()
        # )
        data = request.data
        status = request.status
        print(data)
        print(type(status))
        # print(type(data))
        assert type(data) == str
        assert status in ['failed','success','cancelled']
        data= bytes(data,'ascii')
        digest = hashlib.sha512(data).digest()
        message_to_sign = bytes(digest.hex()+status,'ascii')
        signature = private_key.sign(message_to_sign)
        public_key.verify(signature, message_to_sign)
        print(signature.hex())
        # print(type(status))
        return SignResponse(
            task_id= 'id_place_holder',
            exp_dt = "2025-11-05T14:30:00+07:00",
            signature_hex=signature.hex(),
            status=status
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
