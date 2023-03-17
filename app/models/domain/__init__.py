# ПИЗДЕЦ ГОВНО, Я ЕБАЛ
# https://stackoverflow.com/questions/74346565/fastapi-typeerror-issubclass-arg-1-must-be-a-class-with-modular-imports

# FIXED, НЕ ТРОГАТЬ НЕ ТРОГАТЬ
from .comments import CommentInDB
from .groups import GroupInDB
from .perms import PermissionsInDB, Permissions
from .products import ProductInDB
from .product_lists import ProductListInDB
from .review import ReviewInDB
from .profiles import Profile
from .seller import SellerInDB
from .tag import TagsInDB
from .text_entities import TextEntitiesInDB
from .transaction import MoneyTransactionInDB
from .users import User, UserInDB
from .wallet import Wallet, WalletInDB
from .base import CommentSection

Permissions.update_forward_refs(**locals())
PermissionsInDB.update_forward_refs(**locals())
CommentInDB.update_forward_refs(**locals())
ProductListInDB.update_forward_refs(**locals())
ProductInDB.update_forward_refs(**locals())
GroupInDB.update_forward_refs(**locals())
Wallet.update_forward_refs(**locals())
SellerInDB.update_forward_refs(**locals())
CommentSection.update_forward_refs(**locals())
User.update_forward_refs(**locals())
UserInDB.update_forward_refs(**locals())
