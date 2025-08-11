from . import db
from flask_login import UserMixin
from sqlalchemy import func, event
from slugify import slugify
from sqlalchemy.orm import backref
from datetime import datetime


player_sessions = db.Table(
    'player_sessions',
    db.Column(
        'player_id',
        db.Integer,
        db.ForeignKey('player_character.id', ondelete='CASCADE', name='fk_player_sessions_player_id'),
        primary_key=True
    ),
    db.Column(
        'session_id',
        db.Integer,
        db.ForeignKey('session.id', ondelete='CASCADE', name='fk_player_sessions_session_id'),
        primary_key=True
    )
)
player_magic_items = db.Table(
    'player_magic_items',
    db.Column(
        'player_id',
        db.Integer,
        db.ForeignKey('player_character.id', ondelete='CASCADE', name='fk_player_magic_items_player_id'),
        primary_key=True
    ),
    db.Column(
        'magic_item_id',
        db.Integer,
        db.ForeignKey('magic_item.id', ondelete='CASCADE', name='fk_player_magic_items_magic_item_id'),
        primary_key=True
    )
)
player_quests = db.Table(
    'player_quests',
    db.Column(
        'player_id',
        db.Integer,
        db.ForeignKey('player_character.id', ondelete='CASCADE', name='fk_player_quests_player_id'),
        primary_key=True
    ),
    db.Column(
        'quest_id',
        db.Integer,
        db.ForeignKey('quest.id', ondelete='CASCADE', name='fk_player_quests_quest_id'),
        primary_key=True
    )
)
magicitem_spells = db.Table(
    'magicitem_spells',
    db.Column(
        'magic_item_id',
        db.Integer,
        db.ForeignKey('magic_item.id', ondelete='CASCADE', name='fk_magicitem_spells_magic_item_id'),
        primary_key=True
    ),
    db.Column(
        'spell_id',
        db.Integer,
        db.ForeignKey('spell.id', ondelete='CASCADE', name='fk_magicitem_spells_spell_id'),
        primary_key=True
    )
)
npc_quests = db.Table(
    'npc_quests',
    db.Column(
        'npc_id',
        db.Integer,
        db.ForeignKey('npc.id', ondelete='CASCADE', name='fk_npc_quests_npc_id'),
        primary_key=True
    ),
    db.Column(
        'quest_id',
        db.Integer,
        db.ForeignKey('quest.id', ondelete='CASCADE', name='fk_npc_quests_quest_id'),
        primary_key=True
    )
)
monster_spells = db.Table(
    'monster_spells',
    db.Column(
        'monster_id', 
        db.Integer, 
        db.ForeignKey('monster.id', ondelete='CASCADE', name='fk_monster_spells_monster_id'), 
        primary_key=True
    ),
    db.Column(
        'spell_id', 
        db.Integer, 
        db.ForeignKey('spell.id', ondelete='CASCADE', name='fk_monster_spells_spell_id'), 
        primary_key=True
    )
)

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    name = db.Column(db.String(150))
    is_admin= db.Column(db.Boolean, default=False)
    image = db.Column(db.String(255), nullable=True)
    characters = db.relationship('PlayerCharacter', backref='player', lazy=True)
    def __str__(self):
        return self.name

class Page(db.Model):
    __tablename__ = 'page'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, unique=True)
    slug = db.Column(db.String(200), nullable=False, unique=True)  # URL-friendly
    content = db.Column(db.Text, nullable=True)
    image = db.Column(db.String(255), nullable=True)
    content_md = db.Column(db.Text, nullable=True)
    # Hierarchy
    parent_id = db.Column(db.Integer, db.ForeignKey('page.id'), nullable=True)
    children = db.relationship(
        'Page',
        backref=backref('parent', remote_side=[id]),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    comments = db.relationship('Comment', backref='page', lazy=True, cascade="all, delete-orphan")
    # Optional metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return self.title

    def get_ancestors(self):
        """Returns a list of all parent pages up to the root."""
        ancestors = []
        current = self.parent
        while current:
            ancestors.insert(0, current)
            current = current.parent
        return ancestors

    def get_path(self):
        """Returns the full path from root to this page."""
        return "/".join([ancestor.slug for ancestor in self.get_ancestors()] + [self.slug])

    def get_tree(self):
        """Recursively returns a dictionary representing the page and its children."""
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'children': [child.get_tree() for child in self.children.order_by(Page.title)]
        }

class Comment(db.Model):
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    page_id = db.Column(db.Integer, db.ForeignKey('page.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    comment_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Self-referential relationship for replies
    replies = db.relationship(
        'Comment',
        backref=db.backref('parent', remote_side=[id]),
        lazy=True,
        cascade='all, delete-orphan'
    )
    user = db.relationship('User', backref='comments')

class Spell(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(200), nullable=False, unique=True)
    level = db.Column(db.Integer, nullable=False)
    cast_time = db.Column(db.Integer, default=1)
    range_area = db.Column(db.Integer,default=5)
    components = db.Column(db.String(50),default='V,S')
    duration = db.Column(db.Integer,default=10)
    cooldown = db.Column(db.Integer,default=0)
    school = db.Column(db.String(50),default='Physical')
    effect = db.Column(db.String(50),default='Attack')
    description = db.Column(db.Text, default='Placeholder')
    created_at = db.Column(db.DateTime, default=func.now())
    image = db.Column(db.String(255), nullable=True)
    monsters = db.relationship('Monster', secondary=monster_spells, back_populates='spells')
    items = db.relationship(
        'MagicItem',
        secondary=magicitem_spells,
        back_populates='spells',
        lazy='dynamic'
    )

    def __str__(self):
        return self.name

class Monster(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(200), nullable=False, unique=True)
    description = db.Column(db.Text, default='No description provided.')
    hit_points = db.Column(db.Integer, default=0)
    armor_class = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=func.now())
    image = db.Column(db.String(255), nullable=True)
    spells = db.relationship('Spell', secondary=monster_spells, back_populates='monsters')

    def __str__(self):
        return self.name

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(200), nullable=False, unique=True)
    session_no = db.Column(db.Integer, default=1)
    campaign_name = db.Column(db.String(100), default='The fool\'s legacy')
    session_date = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, default='')
    created_at = db.Column(db.DateTime, default=func.now())
    players = db.relationship(
        'PlayerCharacter',
        secondary=player_sessions,
        back_populates='sessions',
        lazy='dynamic'
    )
    image = db.Column(db.String(255), nullable=True)
    def __str__(self):
        return self.name

class MagicItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(200), nullable=False, unique=True)
    rarity = db.Column(db.String(50),default='Rare')
    type = db.Column(db.String(50),default='Weapon')
    cost = db.Column(db.Integer,default=10)
    description = db.Column(db.Text,default='Placeholder')
    found_in_quest = db.Column(db.Integer, db.ForeignKey('quest.id'))
    created_at = db.Column(db.DateTime, default=func.now())
    players = db.relationship(
        'PlayerCharacter',
        secondary=player_magic_items,
        back_populates='items',
        lazy='dynamic'
    )
    spells = db.relationship(
        'Spell',
        secondary=magicitem_spells,
        back_populates='items',
        lazy='dynamic'
    )

    image = db.Column(db.String(255), nullable=True)
    def __str__(self):
        return self.name

class Quest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), unique=True, nullable=False)
    slug = db.Column(db.String(200), nullable=False, unique=True)
    summary = db.Column(db.Text)
    reward = db.Column(db.Text)
    status = db.Column(db.String(50), default='Not Started')
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    players = db.relationship(
        'PlayerCharacter',
        secondary=player_quests,
        back_populates='quests',
        lazy='dynamic'
    )
    npcs = db.relationship(
        'NPC',
        secondary=npc_quests,
        back_populates='quests',
        lazy='dynamic'
    )
    image = db.Column(db.String(255), nullable=True)
    def __str__(self):
        return self.title

class NPC(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(200), nullable=False, unique=True)
    race = db.Column(db.String(50))
    level = db.Column(db.Integer,default=10)
    role = db.Column(db.String(100))
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=func.now())
    quests = db.relationship(
        'Quest',
        secondary=npc_quests,
        back_populates='npcs',
        lazy='dynamic'
    )
    image = db.Column(db.String(255), nullable=True)
    def __str__(self):
        return self.name

class PlayerCharacter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(200), nullable=False, unique=True)
    race = db.Column(db.String(50))
    character_class = db.Column(db.String(50))
    level = db.Column(db.Integer, default=1)

    # Ability Scores
    strength = db.Column(db.Integer, default=10)
    dexterity = db.Column(db.Integer, default=10)
    constitution = db.Column(db.Integer, default=10)
    intelligence = db.Column(db.Integer, default=10)
    wisdom = db.Column(db.Integer, default=10)
    charisma = db.Column(db.Integer, default=10)

    # Combat Stats
    armor_class = db.Column(db.Integer, default=10)
    initiative = db.Column(db.Integer, default=0)
    speed = db.Column(db.Integer, default=30)
    current_hp = db.Column(db.Integer, default=10)
    max_hp = db.Column(db.Integer, default=10)
    hit_dice = db.Column(db.String(10), default='1d10')

    # Misc
    background = db.Column(db.String(100))
    alignment = db.Column(db.String(50))
    experience_points = db.Column(db.Integer, default=0)
    backstory = db.Column(db.Text)
    notes = db.Column(db.Text)

    # Relationships
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=func.now())
    sessions = db.relationship(
        'Session',
        secondary=player_sessions,
        back_populates='players',
        lazy='dynamic'
    )
    items = db.relationship(
        'MagicItem',
        secondary=player_magic_items,
        back_populates='players',
        lazy='dynamic'
    )
    quests = db.relationship(
        'Quest',
        secondary=player_quests,
        back_populates='players',
        lazy='dynamic'
    )
    image = db.Column(db.String(255), nullable=True)
    def __str__(self):
        return self.name

class Pathway(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    slug = db.Column(db.String(200), nullable=False, unique=True)
    domain = db.Column(db.String(100))  
    description = db.Column(db.Text)
    sequences = db.relationship('Sequence', backref='pathway', lazy=True, cascade="all, delete-orphan")
    image = db.Column(db.String(255), nullable=True)
    def __str__(self):
        return self.name

class Sequence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(200), nullable=False, unique=True)
    ritual = db.Column(db.Text)
    flaw = db.Column(db.Text)
    description = db.Column(db.Text)
    pathway_id = db.Column(db.Integer, db.ForeignKey('pathway.id'), nullable=False)
    image = db.Column(db.String(255), nullable=True)
    def __str__(self):
        return self.title
    

#---------------------------Slugs-------------------------------------
# Single source of truth for model name mapping
MODELS = {
    'player': PlayerCharacter,
    'pathway': Pathway,
    'item': MagicItem,
    'spell': Spell,
    'sequence': Sequence,
    'page': Page,
    'npc': NPC,
    'quest': Quest,
    'monster': Monster,
    'session': Session,
    'user': User,
    'comment':Comment
}
def generate_slug(__mapper, __connection, target):
    # Only proceed if the model has a 'slug' attribute
    if not hasattr(target, 'slug'):
        return
    
    # Pick the attribute to base the slug on
    source_attr = None
    for attr in ['title', 'name']:
        if hasattr(target, attr):
            source_attr = attr
            break

    if source_attr:
        value = getattr(target, source_attr)
        if value:
            # Only update slug if empty or if the source attribute changed (optional)
            target.slug = slugify(value)
# Attach listeners for insert and update for all models you want
for model_class in MODELS.values():
    event.listen(model_class, 'before_insert', generate_slug)
    event.listen(model_class, 'before_update', generate_slug)