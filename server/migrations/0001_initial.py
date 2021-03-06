# -*- coding: utf-8 -*-
# Generated by Django 1.11.17 on 2019-09-19 18:05
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(blank=True, max_length=250, null=True)),
                ('type', models.CharField(choices=[('creature', 'creature'), ('spell', 'spell'), ('player', 'player')], max_length=10)),
                ('family', models.CharField(blank=True, choices=[('beast', 'Beast'), ('demon', 'Demon'), ('undead', 'Undead'), ('elemental', 'Elemental')], max_length=20, null=True)),
                ('cardset', models.CharField(choices=[('set01', 'Basic'), ('set02', 'set02'), ('set03', 'set03'), ('set04', 'set04'), ('set05', 'set05'), ('set06', 'set06'), ('set07', 'set07'), ('set08', 'set08'), ('set09', 'set09'), ('set10', 'The Glory Era'), ('set11', 'set11'), ('set12', 'set12'), ('set13', 'set13'), ('set14', 'set14'), ('set15', 'set15'), ('set16', 'set16'), ('set17', 'set17'), ('set18', 'set18'), ('set19', 'set19'), ('set20', 'set20')], default='set01', max_length=10)),
                ('revenge', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('sacrifice', models.PositiveSmallIntegerField(blank=True, null=True)),
                ('avengeme', models.BooleanField(default=False)),
                ('defender', models.BooleanField(default=False)),
                ('together', models.BooleanField(default=False)),
                ('immune', models.BooleanField(default=False)),
                ('title', models.CharField(max_length=100)),
                ('portrait', models.CharField(blank=True, max_length=100, null=True)),
                ('hp', models.SmallIntegerField(default=0)),
                ('attack', models.SmallIntegerField(default=0)),
                ('mana', models.SmallIntegerField(default=0)),
                ('copy_protected', models.BooleanField(default=False)),
                ('spell_is_harmful', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Deck',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='Beginner', max_length=30)),
                ('card_ids', models.CharField(blank=True, max_length=200, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='decks', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Dungeon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('total_stages', models.IntegerField(default=1)),
                ('cardback_image', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='DungeonStage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('no', models.IntegerField(default=1)),
                ('boss_name', models.CharField(max_length=50)),
                ('boss_hp', models.IntegerField(default=30)),
                ('boss_portrait', models.CharField(max_length=50)),
                ('boss_deck', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='server.Deck')),
                ('dungeon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stages', to='server.Dungeon')),
                ('next_stage', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='next_stages', to='server.DungeonStage')),
            ],
        ),
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='player', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Spell',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('spell_type', models.CharField(choices=[('aura', 'AURA'), ('hp', 'HP'), ('dp', 'DP'), ('hpdp', 'HPDP'), ('damage', 'Damage'), ('swaphpdp', 'Swap Hp <-> Dp'), ('restore', 'Restore'), ('mana', 'Mana'), ('token', 'Token (Target: Champion)'), ('draw', 'Draw'), ('discard', 'Discard (Hand)'), ('shield', 'Shield'), ('tank', 'Tank (Taunt)'), ('greatshield', 'Great Shield'), ('dattack', 'Double Attack'), ('locknloaded', 'Lock & Loaded'), ('returnhand', 'Return to Hand'), ('control', 'Control / Steal'), ('summon', 'Summon'), ('freeze', 'Freeze'), ('attack', 'Auto-Attack'), ('transform', 'Transform'), ('addbuff', 'Add Buff'), ('removebuff', 'Remove Buff'), ('shuffle', 'Shuffle In Deck'), ('execute', 'Execute'), ('dummy', 'Dummy')], max_length=100)),
                ('target_key', models.CharField(choices=[('self', 'Self'), ('owner', 'Card Owner (This Card)'), ('player', 'Player'), ('opponent', 'Opponent'), ('both', 'Player & Opponent'), ('opposite', 'Opposite Player <-> Opponent'), ('destroyer', 'Destroyer (Trigger: destroy)'), ('attacker', 'Attacker (Trigger: attack)'), ('adjacent', 'Adjacent'), ('summons', "Summons (in 'creatures' field)"), ('unique:karamurat', 'unique:karamurat - (My Kara Murat)'), ('aura:owner', 'aura:owner'), ('aura:target', 'aura:target'), ('aura:ground:infected:', 'aura:ground:infected'), ('', ''), ('', '########### BOTH SIDE ###########'), ('both:ground:all', 'both:ground:all'), ('both:ground:random:', 'both:ground:random'), ('both:ground:all:damaged', 'both:ground:all:damaged'), ('both:ground:random:damaged', 'both:ground:random:damaged'), ('both:ground:all:undamaged', 'both:ground:all:undamaged'), ('both:ground:random:undamaged', 'both:ground:random:undamaged'), ('both:ground:selected', 'both:ground:selected'), ('both:ground:selected:creature', 'both:ground:selected:creature'), ('both:ground:selected:damaged', 'both:ground:selected:damaged'), ('both:ground:selected:undamaged', 'both:ground:selected:undamaged'), ('', ''), ('', '########### PLAYER ###########'), ('player:hand:random', 'player:hand:random'), ('player:hand:all', 'player:hand:all'), ('player:deck:random', 'player:deck:random'), ('player:deck:all', 'player:deck:all'), ('player:ground:random', 'player:ground:random'), ('player:ground:all', 'player:ground:all'), ('player:ground:random:damaged', 'player:ground:random:damaged'), ('player:ground:all:damaged', 'player:ground:all:damaged'), ('player:ground:random:undamaged', 'player:ground:random:undamaged'), ('player:ground:all:undamaged', 'player:ground:all:undamaged'), ('player:ground:selected', 'player:ground:selected'), ('player:ground:selected:creature', 'player:ground:selected:creature'), ('player:ground:selected:damaged', 'player:ground:selected:damaged'), ('player:ground:selected:undamaged', 'player:ground:selected:undamaged'), ('', ''), ('', '########### OPPONENT ###########'), ('opponent:hand:random', 'opponent:hand:random'), ('opponent:hand:all', 'opponent:hand:all'), ('opponent:deck:random', 'opponent:deck:random'), ('opponent:deck:all', 'opponent:deck:all'), ('opponent:ground:random', 'opponent:ground:random'), ('opponent:ground:all', 'opponent:ground:all'), ('opponent:ground:random:damaged', 'opponent:ground:random:damaged'), ('opponent:ground:all:damaged', 'opponent:ground:all:damaged'), ('opponent:ground:random:undamaged', 'opponent:ground:random:undamaged'), ('opponent:ground:all:undamaged', 'opponent:ground:all:undamaged'), ('opponent:ground:selected', 'opponent:ground:selected'), ('opponent:ground:selected:creature', 'opponent:ground:selected:creature'), ('opponent:ground:selected:damaged', 'opponent:ground:selected:damaged'), ('opponent:ground:selected:undamaged', 'opponent:ground:selected:undamaged')], max_length=100)),
                ('trigger_key', models.CharField(choices=[('play', 'Play Spell Card'), ('deploy', 'Deploy'), ('draw', 'Draw (This Card)'), ('discard', 'Discard (This Card)'), ('destroy', 'Destroy'), ('amp', 'Anger Management'), ('htp', 'Healing Touch'), ('defense', 'Defense - This Card'), ('attack', 'Attack - This Card'), ('restore', 'Whenever Heal'), ('player:turn:begin', "Beginning of Player's Turn"), ('player:turn:end', "End of Player's Turn"), ('turn:begin', 'Beginning of a Turn'), ('turn:end', 'End of a Turn'), ('', '---- AURA ----'), ('auraPlay', 'onAuraPlay'), ('auraDestroy', 'onAuraDestroy'), ('auraHeal', 'onAuraHeal'), ('auraDefense', 'onAuraDefense'), ('auraAttack', 'onAuraAttack'), ('auraDraw', 'onAuraDraw'), ('auraDiscard', 'onAuraDiscard'), ('auraSummon', 'onAuraSummon')], max_length=100)),
                ('animation', models.CharField(blank=True, max_length=20, null=True)),
                ('desc', models.CharField(blank=True, max_length=200, null=True)),
                ('hp', models.SmallIntegerField(blank=True, null=True)),
                ('dp', models.SmallIntegerField(blank=True, null=True)),
                ('amount', models.SmallIntegerField(blank=True, null=True)),
                ('aura_condition', models.TextField(blank=True, null=True)),
                ('aura_give', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='aura_gives', to='server.Spell')),
                ('aura_take', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='aura_takes', to='server.Spell')),
                ('summon', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='server.Card')),
            ],
        ),
        migrations.AddField(
            model_name='card',
            name='spells',
            field=models.ManyToManyField(blank=True, to='server.Spell'),
        ),
    ]
