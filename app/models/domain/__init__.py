# ПИЗДЕЦ ГОВНО, Я ЕБАЛ
# https://stackoverflow.com/questions/74346565/fastapi-typeerror-issubclass-arg-1-must-be-a-class-with-modular-imports
from .comments import CommentInDB
from .groups import GroupInDB
from .perms import PermissionsInDB
from .products import ProductInDB
from .product_lists import ProductList
from .review import ReviewInDB
from .profiles import Profile
from .seller import SellerInDB
from .tag import TagsInDB, Tag
from .text_entities import TextEntitiesInDB
from .transaction import MoneyTransactionInDB
from .users import User, UserInDB
from .wallet import Wallet, WalletInDB
from .base import CommentSection

ProductList.update_forward_refs(**locals())
ProductInDB.update_forward_refs(**locals())
GroupInDB.update_forward_refs(**locals())
Wallet.update_forward_refs(**locals())
SellerInDB.update_forward_refs(**locals())
CommentSection.update_forward_refs(**locals())
User.update_forward_refs(**locals())
UserInDB.update_forward_refs(**locals())
