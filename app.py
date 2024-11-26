def generate_summary(text: str) -> str:
    """Generate engaging summaries using few-shot examples"""
    chunks = chunk_text(text, chunk_size=8000)
    summaries = []
    
    example_prompt = """Here are two examples of good D&D summaries:

Example 1:
QUEST STATUS: The party encountered goblins in the forest. Sarah's wizard cast fireball for 24 damage, killing 5. Tom's fighter missed twice but hit for 12. Goblins fled, dropping 50 gold.

Summary 1:
QUEST STATUS:
Our adventurers' forest expedition met a goblin war party. Quick thinking and quicker spells sent the survivors fleeing into the underbrush.

BATTLE REPORT:
- Sarah's fireball: 24 damage, 5 goblins eliminated
- Tom's greatsword: Two misses, then hit for 12 damage
- Enemy response: Remaining goblins fled
- Loot: 50 gold recovered

Example 2:
QUEST STATUS: Jack's rogue triggered a trap (8 poison damage). Mary healed 7 points. Found secret wizard's study with spellbook and crystal.

Summary 2:
QUEST STATUS:
Dungeon exploration revealed hidden dangers and arcane secrets.

BATTLE REPORT:
- Trap damage: 8 poison to Jack
- Mary's healing: Restored 7 HP
- Discoveries: Hidden study, spellbook, mysterious crystal

Now summarize this session in a similar style:"""
    
    for chunk in chunks:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            temperature=0.2,
            messages=[
                {"role": "system", "content": "You are an experienced D&D Dungeon Master creating entertaining and accurate session summaries. Include specific numbers, preserve character quirks, and maintain the game's humor while being factual."},
                {"role": "user", "content": f"{example_prompt}\n\n{chunk}"}
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
