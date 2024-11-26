def generate_summary(text: str) -> str:
    """Generate engaging summaries using few-shot examples"""
    chunks = chunk_text(text, chunk_size=8000)
    summaries = []
    
    for chunk in chunks:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=0.2,
            messages=[
                {"role": "system", "content": """You are an experienced D&D Dungeon Master creating session summaries. Match the style and energy of these examples while maintaining accuracy."""},
                {"role": "user", "content": """Example session text:
The party encountered a group of goblins in the forest. Sarah's wizard cast fireball, dealing 24 damage and killing 5 goblins. Tom's fighter missed twice with his greatsword but finally landed a hit for 12 damage. The remaining goblins fled, dropping a pouch with 50 gold."""},
                {"role": "assistant", "content": """QUEST STATUS:
Our adventurers' forest expedition took an exciting turn with an explosive goblin encounter. The party's aggressive response sent the survivors fleeing into the underbrush, leaving behind a tempting reward.

BATTLE REPORT:
Sarah unleashed a devastating fireball into the goblin ranks, the arcane explosion dealing a mighty 24 damage and instantly incinerating five of the creatures. Tom struggled to find his rhythm with his greatsword, watching two mighty swings cut only air before finally connecting for 12 damage, sending another goblin to meet their god.

PARTY HIGHLIGHTS:
- Sarah (Wizard): Demonstrated her mastery of the arcane with a perfectly placed fireball
- Tom (Fighter): Persevered through early misses to land a decisive blow

EXPLORATION & DISCOVERIES:
- Location: Dense forest area
- Loot: Recovered 50 gold from a dropped goblin pouch
- Tactical note: The goblins showed self-preservation instinct, fleeing rather than fighting to the death

CURRENT STATUS:
The party stands victorious in the forest clearing, with fleeing goblins potentially alerting others in the area. The recent combat revealed both the party's strengths and areas for tactical improvement."""},
                {"role": "user", "content": """Example session text:
Jack's rogue failed his perception check and triggered a trap, taking 8 poison damage. Mary's cleric used cure wounds, healing 7 points. The party found a secret door behind a bookshelf, leading to a wizard's study. Inside, they discovered a spellbook and a mysterious crystal."""},
                {"role": "assistant", "content": """QUEST STATUS:
Delving deeper into the dungeon, our adventurers' careful exploration was punctuated by a nasty trap surprise, though quick healing kept the party in fighting form. Their persistence paid off with the discovery of a hidden arcane workspace.

BATTLE REPORT:
- Trap damage: 8 poison damage to Jack
- Healing: Mary's Cure Wounds restored 7 hit points

PARTY HIGHLIGHTS:
- Jack (Rogue): Learned the hard way about this dungeon's defenses, taking a poisoned dart to the shoulder
- Mary (Cleric): Proved her worth with timely healing magic, nearly negating the trap damage

EXPLORATION & DISCOVERIES:
- Found hidden door concealed by bookshelf
- Discovered wizard's private study
- Recovered: Spellbook and unusual crystal
- Environmental detail: Sophisticated hiding mechanism suggests a wealthy or paranoid former resident

CURRENT STATUS:
The party has secured the wizard's study and can now examine their newfound treasures in detail, though questions remain about the crystal's purpose and the study's former occupant."""},
                {"role": "user", "content": f"Now summarize this session:\n{chunk}"}
            ]
        )
        summaries.append(response.choices[0].message.content)
    
    if len(summaries) > 1:
        combined_summary = "\n\n".join(summaries)
        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=0.2,
            messages=[
                {"role": "system", "content": "Combine these summaries into one cohesive narrative, maintaining the engaging style while preserving all specific details, numbers, and character moments."},
                {"role": "user", "content": combined_summary}
            ]
        )
        return response.choices[0].message.content
    
    return summaries[0]
