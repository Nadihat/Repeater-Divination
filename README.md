# Repeater Divination
The Intention Repeater Tarot by Thomas Sweet/AnthroHeart (https://intentionrepeater.boards.net; https://github.com/tsweet77/openrouter-tarot) was translated by Gemini CLI (Pro 2.5) into Lenormand, Runes, Astrology, Kabbalah and probably others to come. Enjoy!

A Lenormand Grand Tableau file was attempted, but it didn't feel like a good divinatory method. Likewise, Geomancy's 15 "drawables" felt too slanted to negativity, and I-CHING3.py recommended me to delete it, so I did.

August 22 Update: `tarot_reader.py` was made by 4.1 Opus and uses SHA256-PBKDF2-HMAC rather than plain SHA512. `"The formula is essentially HMAC(password, salt + iteration_count)"` which is richer for free compared to the older methods. It also supports piped input, does reversals and "verifies its output".

All older files are obsolete and will be upgraded with the new mechanisms soon.

nots_tarot.py experimentally removes the timestamp, since MultiHasher and WordFinder do not use it, and multi.py generated an entire deck and asks you to manually reveal each card by hash. multiv2.py added a status update.

multiv3.py added the ability to draw 1, 3, or 10 cards, reversals with the -r flag, and a final overview. multiv4.py made it so that you must type 3 or more hash prefix characters. v5 added the original query in the overview.

TAROT.py was further beautified/cleaned up by GPT5. AnthroHeart/@Anthro really likes it.<br>
I-CHING.py is the equivalent for I-Ching. I-CHING2.py "Ok, made an update so that it always displays text in the Image, and it keeps up the animation message until drawn." I-CHING3.py is more detailed, but you may prefer to use 2 instead. Your choice.

KABBALAH2.py is MKabbalahv6a.py translated to the new system. KABBALAH3.py was made "automatic" like I-CHING3.py is. You can choose to use it or not.<br>
KABBALAH4.py becomes like I-CHING3.py: varying results by timestamp.

Likewise for RUNES.py.

ANTHRO_ORACLE.py draws animal totems. It isn't automatic.

---

A most interesting note is that symmetrical runes (that look the same any side) such as Gebo do not have a reversed form.

MKabbalahv2.py was 888k `THINK_DEPTH` and contained Excessive (too much) and Deficient (too little) Sephiroth. This gives in total 30 possible meanings for each slot and is I believe better than involving the Qlippoth (the evil side). This version doesn't have the Lightning Flash (the proper order that is always the same) 

MKabbalahv3.py shifted the B/E/D rate to 50/25/25.<br>
MKabbalahv4.py added the 22 Paths.<br>
MKabbalahv5.py added a Variable Path Reading.<br>
MKabbalahv6.py added the Horizontal Reading (Archetypal/Creative/Formative/Material)<br>
MKabbalahv6a.py added the 4 Worlds (Horizontal) as 1 option.<br>

August 1, 2025: Added 2Astrology.py, which contains Transits.
5Astrology.py contains Parallels and Conjunctions (sextiles, squares etc)

6Astrology.py includes Ceres, Juno, Vesta... Eris, Makemake, Gonggong etc. This produces an extraordinary information volume: if you don't need these smaller bodies (as they can muddle up a reading by inventing wrong details about wounds [Ceres iirc], etc), use 5Astrology.py.

cio.py is a non-interactive experiment in generating hashed readings from the AnthroHeart Cio Saga.

RepeatTarot.py includes repeated cards.

The Tarot file is GPL3, and since all the other files were derived from it, they're too.
