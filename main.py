from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from models import Base
from database import engine, AsyncSessionLocal
from pydantic import BaseModel
import crud
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# Import the Prometheus instrumentator
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Initialize and expose Prometheus metrics at /metrics endpoint
    

# Health-check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

class PolicyholderCreate(BaseModel):
    name: str
    email: str
    password: str

class PolicyholderUpdate(BaseModel):
    name: str
    email: str
    password: str

class PolicyCreate(BaseModel):
    coverage: float

class PolicyUpdate(BaseModel):
    coverage: float
    status: str

class ClaimCreate(BaseModel):
    amount: float

class ClaimUpdate(BaseModel):
    status: str

class Loginid(BaseModel):
    id: int
    password: int

@app.post("/")
async def login(data: Loginid, db: AsyncSession = Depends(get_db)):
    return await crud.login(db, data.id, data.password)

@app.post("/signup/")
async def create_policyholder(data: PolicyholderCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_policyholder(db, data.name, data.email, data.password)

@app.put("/policyholders/{policyholder_id}")
async def update_policyholder(policyholder_id: int, data: PolicyholderUpdate, db: AsyncSession = Depends(get_db)):
    return await crud.update_policyholder(db, policyholder_id, data.name, data.email, data.password)

@app.post("/policyholders/{policyholder_id}/policies/")
async def create_policy(policyholder_id: int, data: PolicyCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_policy(db, policyholder_id, data.coverage)

@app.put("/policyholders/{policyholder_id}/policies/{policy_id}")
async def update_policy(policyholder_id: int, policy_id: int, data: PolicyUpdate, db: AsyncSession = Depends(get_db)):
    return await crud.update_policy(db, policyholder_id, policy_id, data.coverage, data.status)

@app.delete("/policyholders/{policyholder_id}/policies/{policy_id}")
async def delete_policy(policyholder_id: int, policy_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.delete_policy(db, policyholder_id, policy_id)

@app.post("/policyholders/{policyholder_id}/claims/{policy_id}")
async def create_claim(policyholder_id: int, policy_id: int, data: ClaimCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_claim(db, policyholder_id, policy_id, data.amount)

@app.put("/policyholders/{policyholder_id}/claims/{policy_id}/{claim_id}")
async def update_claim_status(
    policyholder_id: int, policy_id: int, claim_id: int, data: ClaimUpdate, db: AsyncSession = Depends(get_db)
):
    return await crud.update_claim_status(db, policyholder_id, policy_id, claim_id, data.status)

@app.delete("/policyholders/{policyholder_id}/claims/{policy_id}/{claim_id}")
async def delete_claim(policyholder_id: int, policy_id: int, claim_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.delete_claim(db, policyholder_id, policy_id, claim_id)

@app.delete("/policyholders/{policyholder_id}")
async def delete_policyholder(policyholder_id: int, db: AsyncSession = Depends(get_db)):
    return await crud.delete_policyholder(db, policyholder_id)

@app.get("/policyholders/policies_and_claims")
async def get_all_policies_and_claims(db: AsyncSession = Depends(get_db)):
    try:
        return await crud.get_all_policyholders(db)
    except Exception as e:
        print(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching policies and claims: {str(e)}")

@app.get("/policyholders/{policyholder_id}/policies")
async def get_policies_by_policyholder_endpoint(policyholder_id: int, db: AsyncSession = Depends(get_db)):
    try:
        policies = await crud.get_policies_by_policyholder(db, policyholder_id)
        return {
            "policyholder_id": policyholder_id,
            "policies": policies
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching policies: {str(e)}")

@app.get("/policyholders/{policyholder_id}/claims")
async def get_claims_by_policyholder_endpoint(policyholder_id: int, db: AsyncSession = Depends(get_db)):
    try:
        claims = await crud.get_claims_by_policyholder(db, policyholder_id)
        return {
            "policyholder_id": policyholder_id,
            "claims": claims
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching claims: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
