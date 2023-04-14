# ПИЗДЕЦ ГОВНО, Я ЕБАЛ
# https://stackoverflow.com/questions/74346565/fastapi-typeerror-issubclass-arg-1-must-be-a-class-with-modular-imports

# FIXED, НЕ ТРОГАТЬ НЕ ТРОГАТЬ
# ТРОГАТЬ ТОЛЬКО ПРИ ДОБАВЛЕНИИ МОДЕЛЕЙ КОТОРЫЕ ИМЕЮТ СВЯЗИ
# ПРИ ПОЯВЛЕНИИ ПРОБЛЕМ СВЯЗАННЫЕ СО ForwardRef
# ДОБОВЛЯЕТЕ В ЭТО МЕСТО
from .category import CategoryInDB
from .comments import CommentInDB
from .groups import GroupInDB, Groups
from .perms import PermissionsInDB
from .products import ProductInDB
from .product_lists import ProductListInDB
from .review import ReviewInDB
from .profiles import Profile
from .seller import SellerInDB, ProductSellerInDB
from .tag import TagsInDB
from .text_entities import TextEntitiesInDB
from .transaction import MoneyTransactionInDB
from .users import User, UserInDB
from .wallet import Wallet, WalletInDB
from .base import CommentSection


__all__ = (
    "CategoryInDB",
    "CommentInDB",
    "GroupInDB",
    "Groups",
    "PermissionsInDB",
    "ProductInDB",
    "ProductListInDB",
    "ReviewInDB",
    "Profile",
    "SellerInDB",
    "ProductSellerInDB",
    "TagsInDB",
    "TextEntitiesInDB",
    "MoneyTransactionInDB",
    "User",
    "UserInDB",
    "Wallet",
    "WalletInDB",
    "CommentSection",
)

PermissionsInDB.update_forward_refs(**locals())
CommentInDB.update_forward_refs(**locals())
ProductListInDB.update_forward_refs(**locals())
ProductInDB.update_forward_refs(**locals())
GroupInDB.update_forward_refs(**locals())
Wallet.update_forward_refs(**locals())
SellerInDB.update_forward_refs(**locals())
ProductSellerInDB.update_forward_refs(**locals())
CommentSection.update_forward_refs(**locals())
User.update_forward_refs(**locals())
UserInDB.update_forward_refs(**locals())
Groups.update_forward_refs(**locals())
CategoryInDB.update_forward_refs(**locals())
