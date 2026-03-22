"""Asset CRUD endpoints — full implementation for all 15 asset types."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime

from database import get_db
from routers.auth import get_current_user
from models.user import User
from models.mutual_fund import MutualFundHolding, MutualFundTransaction
from models.stock import StockHolding, StockTransaction
from models.deposit import Deposit
from models.provident_fund import ProvidentFund
from models.sukanya_samriddhi import SukanyaSamriddhi
from models.nps import NPS
from models.gold import GoldHolding
from models.real_estate import RealEstate
from models.international_holding import InternationalHolding
from models.crypto import CryptoHolding
from models.post_office import PostOfficeScheme
from models.goal import Goal
from models.savings_account import SavingsAccount

router = APIRouter(prefix="/api/assets", tags=["assets"])


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def row_to_dict(row):
    return {c.name: getattr(row, c.name) for c in row.__table__.columns}


# ===========================================================================
# 1. Mutual-Fund Holdings
# ===========================================================================

class MutualFundHoldingCreate(BaseModel):
    profile_id: int
    folio_number: str
    scheme_name: str
    scheme_code: Optional[str] = None
    amc_name: Optional[str] = None
    units_held: float
    avg_nav: Optional[float] = None
    current_nav: Optional[float] = None
    invested_amount: Optional[float] = None
    current_value: Optional[float] = None


class MutualFundHoldingUpdate(BaseModel):
    profile_id: Optional[int] = None
    folio_number: Optional[str] = None
    scheme_name: Optional[str] = None
    scheme_code: Optional[str] = None
    amc_name: Optional[str] = None
    units_held: Optional[float] = None
    avg_nav: Optional[float] = None
    current_nav: Optional[float] = None
    invested_amount: Optional[float] = None
    current_value: Optional[float] = None


@router.get("/mutual-funds")
def list_mutual_funds(
    profile_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(MutualFundHolding)
    if profile_id is not None:
        q = q.filter(MutualFundHolding.profile_id == profile_id)
    return [row_to_dict(r) for r in q.all()]


@router.post("/mutual-funds")
def create_mutual_fund(
    body: MutualFundHoldingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = MutualFundHolding(**body.dict())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.put("/mutual-funds/{item_id}")
def update_mutual_fund(
    item_id: int,
    body: MutualFundHoldingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(MutualFundHolding).filter(MutualFundHolding.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    for field, value in body.dict(exclude_none=True).items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.delete("/mutual-funds/{item_id}", status_code=204)
def delete_mutual_fund(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(MutualFundHolding).filter(MutualFundHolding.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(row)
    db.commit()


# ===========================================================================
# 2. Mutual-Fund Transactions
# ===========================================================================

class MutualFundTransactionCreate(BaseModel):
    profile_id: int
    folio_number: str
    transaction_date: datetime
    transaction_type: str
    units: Optional[float] = None
    nav: Optional[float] = None
    amount: Optional[float] = None
    cas_source_file: Optional[str] = None


class MutualFundTransactionUpdate(BaseModel):
    profile_id: Optional[int] = None
    folio_number: Optional[str] = None
    transaction_date: Optional[datetime] = None
    transaction_type: Optional[str] = None
    units: Optional[float] = None
    nav: Optional[float] = None
    amount: Optional[float] = None
    cas_source_file: Optional[str] = None


@router.get("/mutual-fund-transactions")
def list_mutual_fund_transactions(
    profile_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(MutualFundTransaction)
    if profile_id is not None:
        q = q.filter(MutualFundTransaction.profile_id == profile_id)
    return [row_to_dict(r) for r in q.all()]


@router.post("/mutual-fund-transactions")
def create_mutual_fund_transaction(
    body: MutualFundTransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = MutualFundTransaction(**body.dict())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.put("/mutual-fund-transactions/{item_id}")
def update_mutual_fund_transaction(
    item_id: int,
    body: MutualFundTransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(MutualFundTransaction).filter(MutualFundTransaction.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    for field, value in body.dict(exclude_none=True).items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.delete("/mutual-fund-transactions/{item_id}", status_code=204)
def delete_mutual_fund_transaction(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(MutualFundTransaction).filter(MutualFundTransaction.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(row)
    db.commit()


# ===========================================================================
# 3. Stock Holdings
# ===========================================================================

class StockHoldingCreate(BaseModel):
    profile_id: int
    exchange: str = "NSE"
    ticker: str
    company_name: Optional[str] = None
    isin: Optional[str] = None
    quantity: float
    avg_buy_price: Optional[float] = None
    current_price: Optional[float] = None
    broker: Optional[str] = None


class StockHoldingUpdate(BaseModel):
    profile_id: Optional[int] = None
    exchange: Optional[str] = None
    ticker: Optional[str] = None
    company_name: Optional[str] = None
    isin: Optional[str] = None
    quantity: Optional[float] = None
    avg_buy_price: Optional[float] = None
    current_price: Optional[float] = None
    broker: Optional[str] = None


@router.get("/stocks")
def list_stocks(
    profile_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(StockHolding)
    if profile_id is not None:
        q = q.filter(StockHolding.profile_id == profile_id)
    return [row_to_dict(r) for r in q.all()]


@router.post("/stocks")
def create_stock(
    body: StockHoldingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = StockHolding(**body.dict())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.put("/stocks/{item_id}")
def update_stock(
    item_id: int,
    body: StockHoldingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(StockHolding).filter(StockHolding.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    for field, value in body.dict(exclude_none=True).items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.delete("/stocks/{item_id}", status_code=204)
def delete_stock(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(StockHolding).filter(StockHolding.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(row)
    db.commit()


# ===========================================================================
# 4. Stock Transactions
# ===========================================================================

class StockTransactionCreate(BaseModel):
    profile_id: int
    ticker: str
    transaction_date: datetime
    action: str
    quantity: float
    price: float
    brokerage: Optional[float] = 0.0
    notes: Optional[str] = None


class StockTransactionUpdate(BaseModel):
    profile_id: Optional[int] = None
    ticker: Optional[str] = None
    transaction_date: Optional[datetime] = None
    action: Optional[str] = None
    quantity: Optional[float] = None
    price: Optional[float] = None
    brokerage: Optional[float] = None
    notes: Optional[str] = None


@router.get("/stock-transactions")
def list_stock_transactions(
    profile_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(StockTransaction)
    if profile_id is not None:
        q = q.filter(StockTransaction.profile_id == profile_id)
    return [row_to_dict(r) for r in q.all()]


@router.post("/stock-transactions")
def create_stock_transaction(
    body: StockTransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = StockTransaction(**body.dict())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.put("/stock-transactions/{item_id}")
def update_stock_transaction(
    item_id: int,
    body: StockTransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(StockTransaction).filter(StockTransaction.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    for field, value in body.dict(exclude_none=True).items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.delete("/stock-transactions/{item_id}", status_code=204)
def delete_stock_transaction(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(StockTransaction).filter(StockTransaction.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(row)
    db.commit()


# ===========================================================================
# 5. Deposits (FD / RD)
# ===========================================================================

class DepositCreate(BaseModel):
    profile_id: int
    type: str = "FD"
    bank_name: str
    branch: Optional[str] = None
    principal_amount: float
    interest_rate: float
    compounding: str = "quarterly"
    start_date: date
    maturity_date: Optional[date] = None
    maturity_amount: Optional[float] = None
    is_joint: bool = False
    joint_holder_name: Optional[str] = None
    nomination: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool = True


class DepositUpdate(BaseModel):
    profile_id: Optional[int] = None
    type: Optional[str] = None
    bank_name: Optional[str] = None
    branch: Optional[str] = None
    principal_amount: Optional[float] = None
    interest_rate: Optional[float] = None
    compounding: Optional[str] = None
    start_date: Optional[date] = None
    maturity_date: Optional[date] = None
    maturity_amount: Optional[float] = None
    is_joint: Optional[bool] = None
    joint_holder_name: Optional[str] = None
    nomination: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None


@router.get("/deposits")
def list_deposits(
    profile_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Deposit)
    if profile_id is not None:
        q = q.filter(Deposit.profile_id == profile_id)
    return [row_to_dict(r) for r in q.all()]


@router.post("/deposits")
def create_deposit(
    body: DepositCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = Deposit(**body.dict())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.put("/deposits/{item_id}")
def update_deposit(
    item_id: int,
    body: DepositUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(Deposit).filter(Deposit.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    for field, value in body.dict(exclude_none=True).items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.delete("/deposits/{item_id}", status_code=204)
def delete_deposit(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(Deposit).filter(Deposit.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(row)
    db.commit()


# ===========================================================================
# 6. Provident Funds (PPF / EPF / GPF / VPF)
# ===========================================================================

class ProvidentFundCreate(BaseModel):
    profile_id: int
    type: str = "PPF"
    account_number: Optional[str] = None
    bank_or_employer: Optional[str] = None
    opening_balance: float = 0.0
    current_balance: float = 0.0
    interest_rate: Optional[float] = None
    maturity_date: Optional[date] = None
    annual_contributions: Optional[str] = None
    employer_contribution: Optional[float] = None


class ProvidentFundUpdate(BaseModel):
    profile_id: Optional[int] = None
    type: Optional[str] = None
    account_number: Optional[str] = None
    bank_or_employer: Optional[str] = None
    opening_balance: Optional[float] = None
    current_balance: Optional[float] = None
    interest_rate: Optional[float] = None
    maturity_date: Optional[date] = None
    annual_contributions: Optional[str] = None
    employer_contribution: Optional[float] = None


@router.get("/provident-funds")
def list_provident_funds(
    profile_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(ProvidentFund)
    if profile_id is not None:
        q = q.filter(ProvidentFund.profile_id == profile_id)
    return [row_to_dict(r) for r in q.all()]


@router.post("/provident-funds")
def create_provident_fund(
    body: ProvidentFundCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = ProvidentFund(**body.dict())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.put("/provident-funds/{item_id}")
def update_provident_fund(
    item_id: int,
    body: ProvidentFundUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(ProvidentFund).filter(ProvidentFund.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    for field, value in body.dict(exclude_none=True).items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.delete("/provident-funds/{item_id}", status_code=204)
def delete_provident_fund(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(ProvidentFund).filter(ProvidentFund.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(row)
    db.commit()


# ===========================================================================
# 7. Sukanya Samriddhi Yojana
# ===========================================================================

class SukanyaSamriddhiCreate(BaseModel):
    profile_id: int
    account_number: Optional[str] = None
    post_office_bank: Optional[str] = None
    date_of_birth_child: Optional[date] = None
    account_opening_date: date
    maturity_date: Optional[date] = None
    current_balance: float = 0.0
    interest_rate: Optional[float] = None
    annual_contributions: Optional[str] = None


class SukanyaSamriddhiUpdate(BaseModel):
    profile_id: Optional[int] = None
    account_number: Optional[str] = None
    post_office_bank: Optional[str] = None
    date_of_birth_child: Optional[date] = None
    account_opening_date: Optional[date] = None
    maturity_date: Optional[date] = None
    current_balance: Optional[float] = None
    interest_rate: Optional[float] = None
    annual_contributions: Optional[str] = None


@router.get("/sukanya-samriddhi")
def list_ssy(
    profile_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(SukanyaSamriddhi)
    if profile_id is not None:
        q = q.filter(SukanyaSamriddhi.profile_id == profile_id)
    return [row_to_dict(r) for r in q.all()]


@router.post("/sukanya-samriddhi")
def create_ssy(
    body: SukanyaSamriddhiCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = SukanyaSamriddhi(**body.dict())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.put("/sukanya-samriddhi/{item_id}")
def update_ssy(
    item_id: int,
    body: SukanyaSamriddhiUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(SukanyaSamriddhi).filter(SukanyaSamriddhi.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    for field, value in body.dict(exclude_none=True).items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.delete("/sukanya-samriddhi/{item_id}", status_code=204)
def delete_ssy(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(SukanyaSamriddhi).filter(SukanyaSamriddhi.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(row)
    db.commit()


# ===========================================================================
# 8. NPS
# ===========================================================================

class NPSCreate(BaseModel):
    profile_id: int
    pran_number: Optional[str] = None
    tier: str = "Tier1"
    fund_manager: Optional[str] = None
    scheme_preference: Optional[str] = None
    equity_pct: Optional[float] = None
    corporate_bond_pct: Optional[float] = None
    govt_bond_pct: Optional[float] = None
    current_nav: Optional[float] = None
    units_held: Optional[float] = None
    current_value: Optional[float] = None
    employer_contribution_annual: Optional[float] = None
    self_contribution_annual: Optional[float] = None


class NPSUpdate(BaseModel):
    profile_id: Optional[int] = None
    pran_number: Optional[str] = None
    tier: Optional[str] = None
    fund_manager: Optional[str] = None
    scheme_preference: Optional[str] = None
    equity_pct: Optional[float] = None
    corporate_bond_pct: Optional[float] = None
    govt_bond_pct: Optional[float] = None
    current_nav: Optional[float] = None
    units_held: Optional[float] = None
    current_value: Optional[float] = None
    employer_contribution_annual: Optional[float] = None
    self_contribution_annual: Optional[float] = None


@router.get("/nps")
def list_nps(
    profile_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(NPS)
    if profile_id is not None:
        q = q.filter(NPS.profile_id == profile_id)
    return [row_to_dict(r) for r in q.all()]


@router.post("/nps")
def create_nps(
    body: NPSCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = NPS(**body.dict())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.put("/nps/{item_id}")
def update_nps(
    item_id: int,
    body: NPSUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(NPS).filter(NPS.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    for field, value in body.dict(exclude_none=True).items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.delete("/nps/{item_id}", status_code=204)
def delete_nps(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(NPS).filter(NPS.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(row)
    db.commit()


# ===========================================================================
# 9. Gold Holdings
# ===========================================================================

class GoldHoldingCreate(BaseModel):
    profile_id: int
    type: str = "physical"
    quantity_grams: Optional[float] = None
    units: Optional[float] = None
    buy_price_per_gram_or_unit: Optional[float] = None
    current_price_per_gram_or_unit: Optional[float] = None
    purchase_date: Optional[date] = None
    sgb_series: Optional[str] = None
    sgb_maturity_date: Optional[date] = None
    sgb_interest_rate: Optional[float] = None
    custodian: Optional[str] = None
    notes: Optional[str] = None


class GoldHoldingUpdate(BaseModel):
    profile_id: Optional[int] = None
    type: Optional[str] = None
    quantity_grams: Optional[float] = None
    units: Optional[float] = None
    buy_price_per_gram_or_unit: Optional[float] = None
    current_price_per_gram_or_unit: Optional[float] = None
    purchase_date: Optional[date] = None
    sgb_series: Optional[str] = None
    sgb_maturity_date: Optional[date] = None
    sgb_interest_rate: Optional[float] = None
    custodian: Optional[str] = None
    notes: Optional[str] = None


@router.get("/gold")
def list_gold(
    profile_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(GoldHolding)
    if profile_id is not None:
        q = q.filter(GoldHolding.profile_id == profile_id)
    return [row_to_dict(r) for r in q.all()]


@router.post("/gold")
def create_gold(
    body: GoldHoldingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = GoldHolding(**body.dict())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.put("/gold/{item_id}")
def update_gold(
    item_id: int,
    body: GoldHoldingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(GoldHolding).filter(GoldHolding.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    for field, value in body.dict(exclude_none=True).items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.delete("/gold/{item_id}", status_code=204)
def delete_gold(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(GoldHolding).filter(GoldHolding.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(row)
    db.commit()


# ===========================================================================
# 10. Real Estate
# ===========================================================================

class RealEstateCreate(BaseModel):
    profile_id: int
    property_name: str
    property_type: str = "residential"
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[float] = None
    registration_cost: Optional[float] = None
    stamp_duty: Optional[float] = None
    other_costs: Optional[float] = None
    current_estimated_value: Optional[float] = None
    outstanding_loan_amount: Optional[float] = None
    rental_income_monthly: Optional[float] = None
    is_joint: bool = False
    joint_holder_name: Optional[str] = None
    notes: Optional[str] = None
    last_valuation_date: Optional[date] = None


class RealEstateUpdate(BaseModel):
    profile_id: Optional[int] = None
    property_name: Optional[str] = None
    property_type: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[float] = None
    registration_cost: Optional[float] = None
    stamp_duty: Optional[float] = None
    other_costs: Optional[float] = None
    current_estimated_value: Optional[float] = None
    outstanding_loan_amount: Optional[float] = None
    rental_income_monthly: Optional[float] = None
    is_joint: Optional[bool] = None
    joint_holder_name: Optional[str] = None
    notes: Optional[str] = None
    last_valuation_date: Optional[date] = None


@router.get("/real-estate")
def list_real_estate(
    profile_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(RealEstate)
    if profile_id is not None:
        q = q.filter(RealEstate.profile_id == profile_id)
    return [row_to_dict(r) for r in q.all()]


@router.post("/real-estate")
def create_real_estate(
    body: RealEstateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = RealEstate(**body.dict())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.put("/real-estate/{item_id}")
def update_real_estate(
    item_id: int,
    body: RealEstateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(RealEstate).filter(RealEstate.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    for field, value in body.dict(exclude_none=True).items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.delete("/real-estate/{item_id}", status_code=204)
def delete_real_estate(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(RealEstate).filter(RealEstate.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(row)
    db.commit()


# ===========================================================================
# 11. International Holdings
# ===========================================================================

class InternationalHoldingCreate(BaseModel):
    profile_id: int
    platform: Optional[str] = None
    ticker: str
    exchange: Optional[str] = None
    company_name: Optional[str] = None
    quantity: float
    avg_buy_price_usd: Optional[float] = None
    current_price_usd: Optional[float] = None
    current_price_inr: Optional[float] = None
    buy_date: Optional[date] = None
    lrs_amount_used: Optional[float] = None


class InternationalHoldingUpdate(BaseModel):
    profile_id: Optional[int] = None
    platform: Optional[str] = None
    ticker: Optional[str] = None
    exchange: Optional[str] = None
    company_name: Optional[str] = None
    quantity: Optional[float] = None
    avg_buy_price_usd: Optional[float] = None
    current_price_usd: Optional[float] = None
    current_price_inr: Optional[float] = None
    buy_date: Optional[date] = None
    lrs_amount_used: Optional[float] = None


@router.get("/international")
def list_international(
    profile_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(InternationalHolding)
    if profile_id is not None:
        q = q.filter(InternationalHolding.profile_id == profile_id)
    return [row_to_dict(r) for r in q.all()]


@router.post("/international")
def create_international(
    body: InternationalHoldingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = InternationalHolding(**body.dict())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.put("/international/{item_id}")
def update_international(
    item_id: int,
    body: InternationalHoldingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(InternationalHolding).filter(InternationalHolding.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    for field, value in body.dict(exclude_none=True).items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.delete("/international/{item_id}", status_code=204)
def delete_international(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(InternationalHolding).filter(InternationalHolding.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(row)
    db.commit()


# ===========================================================================
# 12. Crypto Holdings
# ===========================================================================

class CryptoHoldingCreate(BaseModel):
    profile_id: int
    coin_symbol: str
    coin_name: Optional[str] = None
    exchange: Optional[str] = None
    quantity: float
    avg_buy_price_inr: Optional[float] = None
    current_price_inr: Optional[float] = None


class CryptoHoldingUpdate(BaseModel):
    profile_id: Optional[int] = None
    coin_symbol: Optional[str] = None
    coin_name: Optional[str] = None
    exchange: Optional[str] = None
    quantity: Optional[float] = None
    avg_buy_price_inr: Optional[float] = None
    current_price_inr: Optional[float] = None


@router.get("/crypto")
def list_crypto(
    profile_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(CryptoHolding)
    if profile_id is not None:
        q = q.filter(CryptoHolding.profile_id == profile_id)
    return [row_to_dict(r) for r in q.all()]


@router.post("/crypto")
def create_crypto(
    body: CryptoHoldingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = CryptoHolding(**body.dict())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.put("/crypto/{item_id}")
def update_crypto(
    item_id: int,
    body: CryptoHoldingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(CryptoHolding).filter(CryptoHolding.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    for field, value in body.dict(exclude_none=True).items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.delete("/crypto/{item_id}", status_code=204)
def delete_crypto(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(CryptoHolding).filter(CryptoHolding.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(row)
    db.commit()


# ===========================================================================
# 13. Post Office Schemes
# ===========================================================================

class PostOfficeSchemeCreate(BaseModel):
    profile_id: int
    scheme_type: str
    account_number: Optional[str] = None
    post_office: Optional[str] = None
    principal_amount: float
    interest_rate: float
    start_date: date
    maturity_date: Optional[date] = None
    maturity_amount: Optional[float] = None
    payout_frequency: Optional[str] = None
    notes: Optional[str] = None


class PostOfficeSchemeUpdate(BaseModel):
    profile_id: Optional[int] = None
    scheme_type: Optional[str] = None
    account_number: Optional[str] = None
    post_office: Optional[str] = None
    principal_amount: Optional[float] = None
    interest_rate: Optional[float] = None
    start_date: Optional[date] = None
    maturity_date: Optional[date] = None
    maturity_amount: Optional[float] = None
    payout_frequency: Optional[str] = None
    notes: Optional[str] = None


@router.get("/post-office")
def list_post_office(
    profile_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(PostOfficeScheme)
    if profile_id is not None:
        q = q.filter(PostOfficeScheme.profile_id == profile_id)
    return [row_to_dict(r) for r in q.all()]


@router.post("/post-office")
def create_post_office(
    body: PostOfficeSchemeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = PostOfficeScheme(**body.dict())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.put("/post-office/{item_id}")
def update_post_office(
    item_id: int,
    body: PostOfficeSchemeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(PostOfficeScheme).filter(PostOfficeScheme.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    for field, value in body.dict(exclude_none=True).items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.delete("/post-office/{item_id}", status_code=204)
def delete_post_office(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(PostOfficeScheme).filter(PostOfficeScheme.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(row)
    db.commit()


# ===========================================================================
# 14. Goals
# ===========================================================================

class GoalCreate(BaseModel):
    profile_id: Optional[int] = None
    name: str
    target_amount: float
    target_date: Optional[date] = None
    current_value: Optional[float] = None
    linked_asset_ids: Optional[str] = None
    notes: Optional[str] = None


class GoalUpdate(BaseModel):
    profile_id: Optional[int] = None
    name: Optional[str] = None
    target_amount: Optional[float] = None
    target_date: Optional[date] = None
    current_value: Optional[float] = None
    linked_asset_ids: Optional[str] = None
    notes: Optional[str] = None


@router.get("/goals")
def list_goals(
    profile_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Goal)
    if profile_id is not None:
        q = q.filter(Goal.profile_id == profile_id)
    return [row_to_dict(r) for r in q.all()]


@router.post("/goals")
def create_goal(
    body: GoalCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = Goal(**body.dict())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.put("/goals/{item_id}")
def update_goal(
    item_id: int,
    body: GoalUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(Goal).filter(Goal.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    for field, value in body.dict(exclude_none=True).items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.delete("/goals/{item_id}", status_code=204)
def delete_goal(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(Goal).filter(Goal.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(row)
    db.commit()


# ===========================================================================
# 15. Savings Accounts
# ===========================================================================

class SavingsAccountCreate(BaseModel):
    profile_id: int
    bank_name: str
    account_type: str = "savings"
    account_number_last4: Optional[str] = None
    current_balance: float = 0.0


class SavingsAccountUpdate(BaseModel):
    profile_id: Optional[int] = None
    bank_name: Optional[str] = None
    account_type: Optional[str] = None
    account_number_last4: Optional[str] = None
    current_balance: Optional[float] = None


@router.get("/savings-accounts")
def list_savings_accounts(
    profile_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(SavingsAccount)
    if profile_id is not None:
        q = q.filter(SavingsAccount.profile_id == profile_id)
    return [row_to_dict(r) for r in q.all()]


@router.post("/savings-accounts")
def create_savings_account(
    body: SavingsAccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = SavingsAccount(**body.dict())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.put("/savings-accounts/{item_id}")
def update_savings_account(
    item_id: int,
    body: SavingsAccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(SavingsAccount).filter(SavingsAccount.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    for field, value in body.dict(exclude_none=True).items():
        setattr(row, field, value)
    db.commit()
    db.refresh(row)
    return row_to_dict(row)


@router.delete("/savings-accounts/{item_id}", status_code=204)
def delete_savings_account(
    item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = db.query(SavingsAccount).filter(SavingsAccount.id == item_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(row)
    db.commit()
