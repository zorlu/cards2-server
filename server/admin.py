from django.contrib import admin
from django.db import models
from django.forms import CheckboxSelectMultiple
from server.models import Card, Player, Deck, Spell, Dungeon, DungeonStage


class CardAdmin(admin.ModelAdmin):
    list_display = ['id', 'type', 'family', 'title', 'mana', 'attack', 'hp', 'spell_is_harmful', 'avengeme' ,'defender', 'together', 'sacrifice', 'revenge', 'immune', 'spells_for_admin', 'description_for_admin', 'portrait', 'cardset']
    list_filter = ['type', 'family', 'cardset']
    search_fields = ['title']
    raw_id_fields = ['spells']
    list_editable = ['mana', 'hp', 'attack', 'spell_is_harmful', 'avengeme', 'defender', 'together', 'sacrifice', 'revenge', 'family', 'immune']


class SpellAdmin(admin.ModelAdmin):
    list_display = ['id', 'spell_type', 'target_key', 'trigger_key', 'desc', 'animation', 'hp', 'dp', 'amount', 'aura_give', 'aura_take']
    raw_id_fields = ['aura_give', 'aura_take', 'summon']
    list_filter = ['spell_type', 'trigger_key']


class PlayerAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'name']
    raw_id_fields = ['user']


class DeckAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'name', 'card_count', 'cards_for_admin']
    raw_id_fields = ['user']
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }


class DungeonAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'total_stages', 'cardback_image']

class DungeonStageAdmin(admin.ModelAdmin):
    list_display = ['dungeon', 'no', 'boss_name', 'boss_hp', 'boss_deck', 'next_stage']
    raw_id_fields = ['boss_deck', 'next_stage']


admin.site.register(Card, CardAdmin)
admin.site.register(Spell, SpellAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Deck, DeckAdmin)
admin.site.register(Dungeon, DungeonAdmin)
admin.site.register(DungeonStage, DungeonStageAdmin)
