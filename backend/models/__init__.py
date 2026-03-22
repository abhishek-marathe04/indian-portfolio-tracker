# Models package — import all models here so that database.init_db() can
# reference this package instead of listing every file explicitly.
from models.user import User
from models.profile import Profile
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
from models.price_cache import PriceCache

__all__ = [
    "User",
    "Profile",
    "MutualFundHolding",
    "MutualFundTransaction",
    "StockHolding",
    "StockTransaction",
    "Deposit",
    "ProvidentFund",
    "SukanyaSamriddhi",
    "NPS",
    "GoldHolding",
    "RealEstate",
    "InternationalHolding",
    "CryptoHolding",
    "PostOfficeScheme",
    "Goal",
    "SavingsAccount",
    "PriceCache",
]
