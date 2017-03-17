import requests
import json
import time
import re
import winsound
import base64

# Config
LOAD_FROM_LOCAL_DUMP_FILE = False
PLAY_SOUNDS = True

# Deal Finder Configs
MIN_PROFIT = 3.0
MIN_ROI = 0.05
CURRENT_LEAGUE = "Legacy"

# Prices URL
API_BASE_URL = "http://api.pathofexile.com/public-stash-tabs"
UNIQUE_FLASK_PRICES_URL = "http://cdn.poe.ninja/api/Data/GetUniqueFlaskOverview"
CARD_PRICES_URL = "http://api.poe.ninja/api/Data/GetDivinationCardsOverview"
PROPHECY_PRICES_URL = "http://api.poe.ninja/api/Data/GetProphecyOverview"
UNIQUE_ARMOUR_PRICES_URL = "http://cdn.poe.ninja/api/Data/GetUniqueArmourOverview"
UNIQUE_WEAPON_PRICES_URL = "http://cdn.poe.ninja/api/Data/GetUniqueWeaponOverview"
UNIQUE_MAP_PRICES_URL = "http://api.poe.ninja/api/Data/GetUniqueMapOverview"
CURRENCY_PRICES_URL = "http://cdn.poe.ninja/api/Data/GetCurrencyOverview"

MARKET_PRICES = [{} for _ in range(10)]

# Weapon Lists
AXE1H_LIST = ['Rusted Hatchet','Jade Hatchet','Boarding Axe','Cleaver','Broad Axe','Arming Axe','Decorative Axe','Spectral Axe','Etched Hatchet','Jasper Axe','Tomahawk','Wrist Chopper','War Axe','Chest Splitter','Ceremonial Axe','Wraith Axe','Engraved Hatchet','Karui Axe','Siege Axe','Reaver Axe','Butcher Axe','Vaal Hatchet','Royal Axe','Infernal Axe','Runic Hatchet']
AXE2H_LIST = ['Stone Axe','Jade Chopper','Woodsplitter','Poleaxe','Double Axe','Gilded Axe','Shadow Axe','Dagger Axe','Jasper Chopper','Timber Axe','Headsman Axe','Labrys','Noble Axe','Abyssal Axe','Karui Chopper','Talon Axe','Sundering Axe','Ezomyte Axe','Vaal Axe','Despot Axe','Void Axe','Fleshripper']
BOW_LIST = ['Crude Bow','Short Bow','Long Bow','Composite Bow','Recurve Bow','Bone Bow','Royal Bow','Death Bow','Grove Bow','Reflex Bow','Decurve Bow','Compound Bow','Sniper Bow','Ivory Bow','Highborn Bow','Decimation Bow','Thicket Bow','Steelwood Bow','Citadel Bow','Ranger Bow','Assassin Bow','Spine Bow','Imperial Bow','Harbinger Bow','Maraketh Bow']
CLAW_LIST = ['Nailed Fist','Sharktooth Claw','Awl','Cat\'s Paw','Blinder','Timeworn Claw','Sparkling Claw','Fright Claw','Double Claw','Thresher Claw','Gouger','Tiger\'s Paw','Gut Ripper','Prehistoric Claw','Noble Claw','Eagle Claw','Twin Claw','Great White Claw','Throat Stabber','Hellion\'s Paw','Eye Gouger','Vaal Claw','Imperial Claw','Terror Claw','Gemini Claw']
DAGGER_LIST = ['Glass Shank','Skinning Knife','Carving Knife','Stiletto','Boot Knife','Copper Kris','Skean','Imp Dagger','Flaying Knife','Prong Dagger','Butcher Knife','Poignard','Boot Blade','Golden Kris','Royal Skean','Fiend Dagger','Trisula','Gutting Knife','Slaughter Knife','Ambusher','Ezomyte Dagger','Platinum Kris','Imperial Skean','Demon Dagger','Sai']
MACE1H_LIST = ['Driftwood Club','Tribal Club','Spiked Club','Stone Hammer','War Hammer','Bladed Mace','Ceremonial Mace','Dream Mace','Wyrm Mace','Petrified Club','Barbed Club','Rock Breaker','Battle Hammer','Flanged Mace','Ornate Mace','Phantom Mace','Dragon Mace','Ancestral Club','Tenderizer','Gavel','Legion Hammer','Pernarch','Auric Mace','Nightmare Mace','Behemoth Mace']
MACE2H_LIST = ['Driftwood Maul','Tribal Maul','Mallet','Sledgehammer','Jagged Maul','Brass Maul','Fright Maul','Morning Star','Totemic Maul','Great Mallet','Steelhead','Spiny Maul','Plated Maul','Dread Maul','Solar Maul','Karui Maul','Colossus Mallet','Piledriver','Meatgrinder','Imperial Maul','Terror Maul','Coronal Maul']
SCEPTRE_LIST = ['Driftwood Sceptre','Darkwood Sceptre','Bronze Sceptre','Quartz Sceptre','Iron Sceptre','Ochre Sceptre','Ritual Sceptre','Shadow Sceptre','Grinning Fetish','Horned Sceptre','Sekhem','Crystal Sceptre','Lead Sceptre','Blood Sceptre','Royal Sceptre','Abyssal Sceptre','Stag Sceptre','Karui Sceptre','Tyrant\'s Sekhem','Opal Sceptre','Platinum Sceptre','Vaal Sceptre','Carnal Sceptre','Void Sceptre','Sambar Sceptre']
STAFF_LIST = ['Gnarled Branch','Primitive Staff','Long Staff','Iron Staff','Coiled Staff','Royal Staff','Vile Staff','Crescent Staff','Woodful Staff','Quarterstaff','Military Staff','Serpentine Staff','Highborn Staff','Foul Staff','Moon Staff','Primordial Staff','Lathi','Ezomyte Staff','Maelström Staff','Imperial Staff','Judgement Staff','Eclipse Staff']
SWORD1H_LIST = ['Rusted Sword','Copper Sword','Sabre','Broad Sword','War Sword','Ancient Sword','Elegant Sword','Dusk Blade','Hook Sword','Variscite Blade','Cutlass','Baselard','Battle Sword','Elder Sword','Twilight Blade','Grappler','Gemstone Sword','Corsair Sword','Gladius','Legion Sword','Vaal Blade','Eternal Sword','Midnight Blade','Tiger Hook']
SWORD2H_LIST = ['Corroded Blade','Longsword','Bastard Sword','Two-Handed Sword','Etched Greatsword','Ornate Sword','Spectral Sword','Curved Blade','Butcher Sword','Footman Sword','Highland Blade','Engraved Greatsword','Tiger Sword','Wraith Sword','Lithe Blade','Headman\'s Sword','Reaver Sword','Ezomyte Blade','Vaal Greatsword','Lion Sword','Infernal Sword','Exquisite Blade']
SWORDTHRUST_LIST = ['Rusted Spike','Whalebone Rapier','Battered Foil','Basket Rapier','Jagged Foil','Antique Rapier','Elegant Foil','Thorn Rapier','Smallsword','Wyrmbone Rapier','Burnished Foil','Estoc','Serrated Foil','Primeval Rapier','Fancy Foil','Apex Rapier','Courtesan Sword','Dragonbone Rapier','Tempered Foil','Pecoraro','Spiraled Foil','Vaal Rapier','Jewelled Foil','Harpy Rapier','Dragoon Sword']
WAND_LIST = ['Driftwood Wand','Goat\'s Horn','Carved Wand','Quartz Wand','Spiraled Wand','Sage Wand','Pagan Wand','Faun\'s Horn','Engraved Wand','Crystal Wand','Serpent Wand','Omen Wand','Heathen Wand','Demon\'s Horn Wand','Opal Wand','Tornado Wand','Prophecy Wand','Profane Wand']

# Armour Lists
# Body Armour
STR_BODY_ARMOUR_LIST = ['Plate Vest','Chestplate','Copper Plate','War Plate','Full Plate','Arena Plate','Lordly Plate','Bronze Plate','Battle Plate','Sun Plate','Colosseum Plate','Majestic Plate','Golden Plate','Crusader Plate','Astral Plate','Gladiator Plate','Glorious Plate']
DEX_BODY_ARMOUR_LIST = ['Shabby Jerkin','Strapped Leather','Buckskin Tunic','Wild Leather','Full Leather','Sun Leather','Thief\'s Garb','Eelskin Tunic','Frontier Leather','Glorious Leather','Coronal Leather','Cutthroat\'s Garb','Sharkskin Tunic','Destiny Leather','Exquisite Leather','Zodiac Leather','Assassin\'s Garb']
INT_BODY_ARMOUR_LIST = ['Simple Robe','Silken Vest','Scholar\'s Robe','Silken Garb','Mage\'s Vestment','Silk Robe','Cabalist Regalia','Sage\'s Robe','Silken Wrap','Conjurer\'s Vestment','Spidersilk Robe','Destroyer Regalia','Savant\'s Robe','Necromancer Silks','Occultist\'s Vestment','Widowsilk Robe','Vaal Regalia']
STR_DEX_BODY_ARMOUR_LIST = ['Scale Vest','Light Brigandine','Scale Doublet','Infantry Brigandine','Full Scale Armour','Soldier\'s Brigandine','Field Lamellar','Wyrmscale Doublet','Hussar Brigandine','Full Wyrmscale','Commander\'s Brigandine','Battle Lamellar','Dragonscale Doublet','Desert Brigandine','Full Dragonscale','General\'s Brigandine','Triumphant Lamellar']
STR_INT_BODY_ARMOUR_LIST = ['Chainmail Vest','Chainmail Tunic','Ringmail Coat','Chainmail Doublet','Full Ringmail','Full Chainmail','Holy Chainmail','Latticed Ringmail','Crusader Chainmail','Ornate Ringmail','Chain Hauberk','Devout Chainmail','Loricated Ringmail','Conquest Chainmail','Elegant Ringmail','Saint\'s Hauberk','Saintly Chainmail']
DEX_INT_BODY_ARMOUR_LIST = ['Padded Vest','Oiled Vest','Padded Jacket','Oiled Coat','Scarlet Raiment','Waxed Garb','Bone Armour','Quilted Jacket','Sleek Coat','Crimson Raiment','Lacquered Garb','Crypt Armour','Sentinel Jacket','Varnished Coat','Blood Raiment','Sadist Garb','Carnal Armour']

# Gloves
STR_GLOVES_LIST = ['Iron Gauntlets','Plated Gauntlets','Bronze Gauntlets','Steel Gauntlets','Antique Gauntlets','Ancient Gauntlets','Goliath Gauntlets','Vaal Gauntlets','Titan Gauntlets','Spiked Gauntlets']
DEX_GLOVES_LIST = ['Rawhide Gloves','Goathide Gloves','Deerskin Gloves','Nubuck Gloves','Eelskin Gloves','Sharkskin Gloves','Shagreen Gloves','Stealth Gloves','Slink Gloves','Gripped Gloves']
INT_GLOVES_LIST = ['Wool Gloves','Velvet Gloves','Silk Gloves','Embroidered Gloves','Satin Gloves','Samite Gloves','Conjurer Gloves','Arcanist Gloves','Sorcerer Gloves','Fingerless Silk Gloves']
STR_DEX_GLOVES_LIST = ['Fishscale Gauntlets','Ironscale Gauntlets','Bronzescale Gauntlets','Steelscale Gauntlets','Serpentscale Gauntlets','Wyrmscale Gauntlets','Hydrascale Gauntlets','Dragonscale Gauntlets']
STR_INT_GLOVES_LIST = ['Chain Gloves','Ringmail Gloves','Mesh Gloves','Riveted Gloves','Zealot Gloves','Soldier Gloves','Legion Gloves','Crusader Gloves']
DEX_INT_GLOVES_LIST = ['Wrapped Mitts','Strapped Mitts','Clasped Mitts','Trapper Mitts','Ambush Mitts','Carnal Mitts','Assassin\'s Mitts','Murder Mitts']

# Helmet
STR_HELMET_LIST = ['Iron Hat','Cone Helmet','Barbute Helmet','Close Helmet','Gladiator Helmet','Reaver Helmet','Siege Helmet','Samite Helmet','Ezomyte Burgonet','Royal Burgonet','Eternal Burgonet']
DEX_HELMET_LIST = ['Leather Cap','Tricorne','Leather Hood','Wolf Pelt','Hunter Hood','Noble Tricorne','Ursine Pelt','Silken Hood','Sinner Tricorne','Lion Pelt']
INT_HELMET_LIST = ['Vine Circlet','Iron Circlet','Torture Cage','Tribal Circlet','Bone Circlet','Lunaris Circlet','Steel Circlet','Necromancer Circlet','Solaris Circlet','Mind Cage','Hubris Circlet']
STR_DEX_HELMET_LIST = ['Battered Helm','Sallet','Visored Sallet','Gilded Sallet','Secutor Helm','Fencer Helm','Lacquered Helmet','Fluted Bascinet','Pig-Faced Bascinet','Nightmare Bascinet']
STR_INT_HELMET_LIST = ['Rusted Coif','Soldier Helmet','Great Helmet','Crusader Helmet','Aventail Helmet','Zealot Helmet','Great Crown','Magistrate Crown','Prophet Crown','Praetor Crown','Bone Helmet']
DEX_INT_HELMET_LIST = ['Scare Mask','Plague Mask','Iron Mask','Festival Mask','Golden Mask','Raven Mask','Callous Mask','Regicide Mask','Harlequin Mask','Vaal Mask','Deicide Mask']

# Boots
STR_BOOTS_LIST = ['Iron Greaves','Steel Greaves','Plated Greaves','Reinforced Greaves','Antique Greaves','Ancient Greaves','Goliath Greaves','Vaal Greaves','Titan Greaves']
DEX_BOOTS_LIST = ['Rawhide Boots','Goathide Boots','Deerskin Boots','Nubuck Boots','Eelskin Boots','Sharkskin Boots','Shagreen Boots','Stealth Boots','Slink Boots']
INT_BOOTS_LIST = ['Wool Shoes','Velvet Slippers','Silk Slippers','Scholar Boots','Satin Slippers','Samite Slippers','Conjurer Boots','Arcanist Slippers','Sorcerer Boots']
STR_DEX_BOOTS_LIST = ['Leatherscale Boots','Ironscale Boots','Bronzescale Boots','Steelscale Boots','Serpentscale Boots','Wyrmscale Boots','Hydrascale Boots','Dragonscale Boots','Two-Toned Boots']
STR_INT_BOOTS_LIST = ['Chain Boots','Ringmail Boots','Mesh Boots','Riveted Boots','Zealot Boots','Soldier Boots','Legion Boots','Crusader Boots','Two-Toned Boots']
DEX_INT_BOOTS_LIST = ['Wrapped Boots','Strapped Boots','Clasped Boots','Shackled Boots','Trapper Boots','Ambush Boots','Carnal Boots','Assassin\'s Boots','Murder Boots','Two-Toned Boots']

# Shield
STR_SHIELD_LIST = ['Splintered Tower Shield','Corroded Tower Shield','Rawhide Tower Shield','Cedar Tower Shield','Copper Tower Shield','Reinforced Tower Shield','Painted Tower Shield','Buckskin Tower Shield','Mahogany Tower Shield','Bronze Tower Shield','Girded Tower Shield','Crested Tower Shield','Shagreen Tower Shield','Ebony Tower Shield','Ezomyte Tower Shield','Colossal Tower Shield','Pinnacle Tower Shield']
DEX_SHIELD_LIST = ['Goathide Buckler','Pine Buckler','Painted Buckler','Hammered Buckler','War Buckler','Gilded Buckler','Oak Buckler','Enameled Buckler','Corrugated Buckler','Battle Buckler','Golden Buckler','Ironwood Buckler','Lacquered Buckler','Vaal Buckler','Crusader Buckler','Imperial Buckler']
INT_SHIELD_LIST = ['Twig Spirit Shield','Yew Spirit Shield','Bone Spirit Shield','Tarnished Spirit Shield','Jingling Spirit Shield','Brass Spirit Shield','Walnut Spirit Shield','Ivory Spirit Shield','Ancient Spirit Shield','Chiming Spirit Shield','Thorium Spirit Shield','Lacewood Spirit Shield','Fossilised Spirit Shield','Vaal Spirit Shield','Harmonic Spirit Shield','Titanium Spirit Shield']
STR_DEX_SHIELD_LIST = ['Rotted Round Shield','Fir Round Shield','Studded Round Shield','Scarlet Round Shield','Splendid Round Shield','Maple Round Shield','Spiked Round Shield','Crimson Round Shield','Baroque Round Shield','Teak Round Shield','Spiny Round Shield','Cardial Round Shield','Elegant Round Shield']
STR_INT_SHIELD_LIST = ['Plank Kite Shield','Linden Kite Shield','Reinforced Kite Shield','Layered Kite Shield','Ceremonial Kite Shield','Etched Kite Shield','Steel Kite Shield','Laminated Kite Shield','Angelic Kite Shield','Branded Kite Shield','Champion Kite Shield','Mosaic Kite Shield','Archon Kite Shield']
DEX_INT_SHIELD_LIST = ['Spiked Bundle','Driftwood Spiked Shield','Alloyed Spiked Shield','Burnished Spiked Shield','Ornate Spiked Shield','Redwood Spiked Shield','Compound Spiked Shield','Polished Spiked Shield','Sovereign Spiked Shield','Alder Spiked Shield','Ezomyte Spiked Shield','Mirrored Spiked Shield','Supreme Spiked Shield']

# Acessories
# Amulet
AMULET_LIST = ['Coral Amulet','Paua Amulet','Amber Amulet','Jade Amulet','Lapis Amulet','Gold Amulet','Agate Amulet','Citrine Amulet','Turquoise Amulet','Onyx Amulet','Marble Amulet','Blue Pearl Amulet']

# Rings
RING_LIST = ['Breach Ring','Coral Ring','Iron Ring','Paua Ring','Unset Ring','Sapphire Ring','Topaz Ring','Ruby Ring','Diamond Ring','Gold Ring','Moonstone Ring','Two-Stone Ring','Amethyst Ring','Prismatic Ring','Opal Ring','Steel Ring']

# Belt
BELT_LIST = ['Chain Belt','Rustic Sash','Heavy Belt','Leather Belt','Cloth Belt','Studded Belt','Vanguard Belt','Crystal Belt']

# Quiver
QUIVER_LIST = ['Two-Point Arrow Quiver','Serrated Arrow Quiver','Sharktooth Arrow Quiver','Blunt Arrow Quiver','Fire Arrow Quiver','Broadhead Arrow Quiver','Penetrating Arrow Quiver','Spike-Point Arrow Quiver']

class ITEM_TYPES:
    Normal, Magic, Rare, Unique, Gem, Currency, Card, Quest, Prophecy, Relic = range(10)

def getNinjaPrices(url):
    params = {'league': CURRENT_LEAGUE, 'time': time.strftime("%Y-%m-%d")}
    response = requests.get(url, params = params)
    prices = response.json().get('lines')
    return dict( [i.get('name'), float(i.get('chaosValue')) ] for i in prices )

def getNinjaCurrency(url):
    params = {'league': CURRENT_LEAGUE, 'time': time.strftime("%Y-%m-%d")}
    response = requests.get(url, params = params)
    prices = response.json().get('lines')
    return dict( [i.get('currencyTypeName'), float(i.get('chaosEquivalent')) ] for i in prices )

def getApiPage(page_id=""):
    target = API_BASE_URL
    if (page_id != ""):
        target = target + "?id=" + str(page_id)
       
    response = requests.get(target)
    
    if response.status_code == 200:
        data = response.json()
        dumpToFile(data, 'lastresponse.txt')
        return data
    else:
        raise ConnectionError('API request returned status code {}: {}!'.format(response.status_code, response.reason))

def loadApiPageFromFile(file_name):
    file = open(file_name, 'r', encoding='utf-8')
    text = file.read()
    file.close()
    return json.loads(text)

def getItemCount(stashes):
    count = 0
    for i in range(len(stashes)):
        len(stashes[i]["items"])
    return count

def hasNumbers(string):
    return any(char.isdigit() for char in string)
    
def isSelling(item):
    return "note" in item.keys() and item['note'].startswith('~') and hasNumbers(item['note'])
    
def isSellingBuyout(item):
    return "note" in item.keys() and item['note'].startswith("~b/o")

def getOfferQuantity(offer):
    if offer[1].lstrip('0') == '':
        return 0.0
    else:
        return float(eval(offer[1].lstrip('0')))

def isOfferValid(item):
    if not isSelling(item):
        return False
    
    offer = getItemSellingOffer(item)
    return (offer[0].startswith("~b/o") or offer[0].startswith("~price")) and \
        '/0' not in offer[1] and \
        getOfferQuantity(offer) > 0.0

def getItemSellingOffer(item):
    offer = re.split(r'([-+]?\d?(?:\.)?(?:\/)?\d+(?:\.)?(?:\/)?\d?)', item['note'])
    return [i.strip() for i in offer]

def offer2chaos(offer):
    quantity = getOfferQuantity(offer)
    
    if "chaos" in offer[2]:
        return quantity
    
    if "fus" in offer[2]:
        return  quantity*MARKET_PRICES[ITEM_TYPES.Currency]["Orb of Fusing"]
    
    if "gcp" in offer[2]:
        return  quantity*MARKET_PRICES[ITEM_TYPES.Currency]["Gemcutter's Prism"]
    
    for currency,value in MARKET_PRICES[ITEM_TYPES.Currency].items():
        if offer[2].lower() in currency.lower():
            return quantity*value

def getItemSellingPrice(item):
    return offer2chaos(getItemSellingOffer(item))
 
def getItemTypeLine(item):
    return item["typeLine"]

def getItemName(item):
    name = re.sub(r'<<.*>>', '', item['name'])
    return name

def getItemCompleteName(item):
    itemName = getItemName(item)
    if itemName:
        itemName += ' '
    itemTypeLine = getItemTypeLine(item)
    return '{}{}'.format(itemName,itemTypeLine)

def getItemFrameType(item):
    return item["frameType"]
    
def getItemLeague(item):
    return item["league"]

def isCorrupted(item):
    return item["corrupted"]

def isFlask(item):
    return 'Flask' in getItemCompleteName(item)

def isAcessory(item):
    c = isAmulet(item) or \
        isRing(item) or \
        isBelt(item) or \
        isQuiver(item)
    return c

def isAmulet(item):
    return getItemTypeLine(item) in AMULET_LIST

def isRing(item):
    return getItemTypeLine(item) in RING_LIST

def isBelt(item):
    return getItemTypeLine(item) in BELT_LIST

def isQuiver(item):
    return getItemTypeLine(item) in QUIVER_LIST

def isArmour(item):
    c = isGloves(item) or \
        isBoots(item) or \
        isHelmet(item) or \
        isShield(item) or \
        isBodyArmour(item)
    return c
    
def isBodyArmour(item):
    c = isStrBodyArmour(item) or \
        isDexBodyArmour(item) or \
        isIntBodyArmour(item) or \
        isStrDexBodyArmour(item) or \
        isStrIntBodyArmour(item) or \
        isDexIntBodyArmour(item)
    return c

def isStrBodyArmour(item):
    return getItemTypeLine(item) in STR_BODY_ARMOUR_LIST

def isDexBodyArmour(item):
    return getItemTypeLine(item) in DEX_BODY_ARMOUR_LIST
    
def isIntBodyArmour(item):
    return getItemTypeLine(item) in INT_BODY_ARMOUR_LIST    

def isStrDexBodyArmour(item):
    return getItemTypeLine(item) in STR_DEX_BODY_ARMOUR_LIST

def isStrIntBodyArmour(item):
    return getItemTypeLine(item) in STR_INT_BODY_ARMOUR_LIST
    
def isDexIntBodyArmour(item):
    return getItemTypeLine(item) in DEX_INT_BODY_ARMOUR_LIST

def isGloves(item):
    c = isStrGloves(item) or \
        isDexGloves(item) or \
        isIntGloves(item) or \
        isStrDexGloves(item) or \
        isStrIntGloves(item) or \
        isDexIntGloves(item)
    return c

def isStrGloves(item):
    return getItemTypeLine(item) in STR_GLOVES_LIST

def isDexGloves(item):
    return getItemTypeLine(item) in DEX_GLOVES_LIST

def isIntGloves(item):
    return getItemTypeLine(item) in INT_GLOVES_LIST

def isStrDexGloves(item):
    return getItemTypeLine(item) in STR_DEX_GLOVES_LIST

def isStrIntGloves(item):
    return getItemTypeLine(item) in STR_INT_GLOVES_LIST

def isDexIntGloves(item):
    return getItemTypeLine(item) in DEX_INT_GLOVES_LIST

def isBoots(item):
    c = isStrBoots(item) or \
        isDexBoots(item) or \
        isIntBoots(item) or \
        isStrDexBoots(item) or \
        isStrIntBoots(item) or \
        isDexIntBoots(item)
    return c

def isStrBoots(item):
    return getItemTypeLine(item) in STR_BOOTS_LIST
    
def isDexBoots(item):
    return getItemTypeLine(item) in DEX_BOOTS_LIST
    
def isIntBoots(item):
    return getItemTypeLine(item) in INT_BOOTS_LIST

def isStrDexBoots(item):
    return getItemTypeLine(item) in STR_DEX_BOOTS_LIST

def isStrIntBoots(item):
    return getItemTypeLine(item) in STR_INT_BOOTS_LIST

def isDexIntBoots(item):
    return getItemTypeLine(item) in DEX_INT_BOOTS_LIST

def isHelmet(item):
    c = isStrHelmet(item) or \
        isDexHelmet(item) or \
        isIntHelmet(item) or \
        isStrDexHelmet(item) or \
        isStrIntHelmet(item) or \
        isDexIntHelmet(item)
    return c

def isStrHelmet(item):
    return getItemTypeLine(item) in STR_HELMET_LIST

def isDexHelmet(item):
    return getItemTypeLine(item) in DEX_HELMET_LIST

def isIntHelmet(item):
    return getItemTypeLine(item) in INT_HELMET_LIST

def isStrDexHelmet(item):
    return getItemTypeLine(item) in STR_DEX_HELMET_LIST

def isStrIntHelmet(item):
    return getItemTypeLine(item) in STR_INT_HELMET_LIST

def isDexIntHelmet(item):
    return getItemTypeLine(item) in DEX_INT_HELMET_LIST

def isShield(item):
    c = isStrShield(item) or \
        isDexShield(item) or \
        isIntShield(item) or \
        isStrDexShield(item) or \
        isStrIntShield(item) or \
        isDexIntShield(item)
    return c

def isStrShield(item):
    return getItemTypeLine(item) in STR_SHIELD_LIST

def isDexShield(item):
    return getItemTypeLine(item) in DEX_SHIELD_LIST

def isIntShield(item):
    return getItemTypeLine(item) in INT_SHIELD_LIST

def isStrDexShield(item):
    return getItemTypeLine(item) in STR_DEX_SHIELD_LIST

def isStrIntShield(item):
    return getItemTypeLine(item) in STR_INT_SHIELD_LIST

def isDexIntShield(item):
    return getItemTypeLine(item) in DEX_INT_SHIELD_LIST

def isWeapon(item):
    c = is1HAxe(item) or \
        is2HAxe(item) or \
        isBow(item) or \
        isClaw(item) or \
        isDagger(item) or \
        is1HMace(item) or \
        is2HMace(item) or \
        isSceptre(item) or \
        isStaff(item) or \
        is1HSword(item) or \
        is2HSword(item) or \
        isThrustSword(item) or \
        isWand(item)
    return c

def is1HAxe(item):
    return getItemTypeLine(item) in AXE1H_LIST

def is2HAxe(item):
    return getItemTypeLine(item) in AXE2H_LIST
    
def isBow(item):
    return getItemTypeLine(item) in BOW_LIST
    
def isClaw(item):
    return getItemTypeLine(item) in CLAW_LIST

def isDagger(item):
    return getItemTypeLine(item) in DAGGER_LIST

def is1HMace(item):
    return getItemTypeLine(item) in MACE1H_LIST

def is2HMace(item):
    return getItemTypeLine(item) in MACE2H_LIST

def isSceptre(item):
    return getItemTypeLine(item) in SCEPTRE_LIST
    
def isStaff(item):
    return getItemTypeLine(item) in STAFF_LIST
    
def is1HSword(item):
    return getItemTypeLine(item) in SWORD1H_LIST

def is2HSword(item):
    return getItemTypeLine(item) in SWORD2H_LIST

def isThrustSword(item):
    return getItemTypeLine(item) in SWORDTHRUST_LIST

def isWand(item):
    return getItemTypeLine(item) in WAND_LIST

def isDivinationCard(item):
    return getItemFrameType(item) == ITEM_TYPES.Card

def isUnique(item):
    return getItemFrameType(item) == ITEM_TYPES.Unique

def isLucrative(item):
    return getProfitMargin(item) >= MIN_PROFIT and getROI(item) >= MIN_ROI

def isItemOfInterest(item):
    return isDivinationCard(item) or \
           (isUnique(item) and isFlask(item)) or \
           (isUnique(item) and isWeapon(item)) or \
           (isUnique(item) and isArmour(item))
           
def decodeUserString(string):
    return str(string.encode("utf-8"))[2:-1]

def getStashName(stash):
    return decodeUserString(stash["stash"])

def getCharacterName(stash):
    return decodeUserString(stash["lastCharacterName"])

def getAccountName(stash):
    return decodeUserString(stash["accountName"])

def isEmpty(stash):
    return stash["items"] == []

def getItemMarketPrice(item):
    if isDivinationCard(item):
        if getItemTypeLine(item) in MARKET_PRICES[ITEM_TYPES.Card]:
            return MARKET_PRICES[ITEM_TYPES.Card][getItemTypeLine(item)]
            
    if isUnique(item):
        if getItemName(item) in MARKET_PRICES[ITEM_TYPES.Unique]:
            return MARKET_PRICES[ITEM_TYPES.Unique][getItemName(item)]
        elif getItemCompleteName(item) in MARKET_PRICES[ITEM_TYPES.Unique]:
            return MARKET_PRICES[ITEM_TYPES.Unique][getItemCompleteName(item)]
        else:
            print('Item not in price list! {}'.format(getItemCompleteName(item)))
    
    return 0.0
                
def getTradeInGameMessage(stash, item):
    characterName = getCharacterName(stash)
    itemName = getItemCompleteName(item)
    price = getItemSellingOffer(item)[1]
    currency = getItemSellingOffer(item)[2]
    league = getItemLeague(item)
    stashName = getStashName(stash)
    w = item.get('w')
    h = item.get('h')
    return '@{} Hi, I would like to buy your {} listed for {} {} in {} (stash tab "{}"; position: left {}, top {})'.format(characterName, itemName, price, currency, league, stashName, w, h)

def getTradeInfoMessage(item):
    itemName = getItemCompleteName(item)
    investment = getItemSellingPrice(item)
    profit = getProfitMargin(item)
    roi = getROI(item)
    return '[ I:{:.1f}c / P:{:.1f}c / ROI:{:.2%} / {}{} ]'.format(investment, profit, roi, "CORRUPTED " if isCorrupted(item) else "", itemName)

def isGoodDeal(item):
    return getItemLeague(item) == CURRENT_LEAGUE and \
        not(getItemFrameType(item) == ITEM_TYPES.Currency) and \
        isSelling(item) and \
        isOfferValid(item) and \
        isItemOfInterest(item) and \
        isLucrative(item)

def findDeals(stashes):
    for s in stashes:
        items = s['items']
        for i in items:
            if isGoodDeal(i):
                print("{} {}".format(getTradeInfoMessage(i), getTradeInGameMessage(s, i)))
                    
def createStashDumpFile(npages, starting_page=""):
    nextPageID = starting_page
    StashDump = open('StashDump.txt', 'w')
    for _ in range(npages):
        data = getApiPage(nextPageID)
        StashDump.write(data)
        nextPageID = data['next_change_id']
    StashDump.close()

def getNinjaNextPageId():
    response = requests.get("http://api.poe.ninja/api/Data/GetStats")
    return response.json().get('nextChangeId')

def getProfitMargin(item):
    return getItemMarketPrice(item) - getItemSellingPrice(item)

def getROI(item):
    if getItemSellingPrice(item) == 0:
        return 9999.0
    return getProfitMargin(item)/getItemSellingPrice(item)

def soundAlert():
    if (PLAY_SOUNDS):
        winsound.PlaySound('SystemHand', winsound.SND_ALIAS)

def dumpToFile(data, filename):
    with open(filename, 'w') as outfile:
        json.dump(data, outfile)
        outfile.close()
        
def splashScreen():
    print(base64.b64decode('X19fX19fX19fXyAgICAgX19fX19fX19fX18gICBfX19fX19fX18gICAgICAuX18=').decode("utf-8"))
    print(base64.b64decode('XF9fX19fXyAgIFxfX19fXF8gICBfX19fXy8gIC8gICBfX19fXy8gX19fXyB8X198X19fX18gICBfX19fX19fX19fXw==').decode("utf-8") )
    print(base64.b64decode('IHwgICAgIF9fXy8gIF8gXHwgICAgX18pXyAgIFxfX19fXyAgXCAvICAgIFx8ICBcX19fXyBcXy8gX18gXF8gIF9fIFw=').decode("utf-8") )
    print(base64.b64decode('IHwgICAgfCAgKCAgPF8+ICkgICAgICAgIFwgIC8gICAgICAgIFwgICB8ICBcICB8ICB8Xz4gPiAgX19fL3wgIHwgXC8=').decode("utf-8") )
    print(base64.b64decode('IHxfX19ffCAgIFxfX19fL19fX19fX18gIC8gL19fX19fX18gIC9fX198ICAvX198ICAgX18vIFxfX18gID5fX3w=').decode("utf-8") )
    print(base64.b64decode('ICAgICAgICAgICAgICAgICAgICAgICBcLyAgICAgICAgICBcLyAgICAgXC8gICB8X198ICAgICAgICBcLw==').decode("utf-8") )
    print()

def loadMarketPrices():
    MARKET_PRICES[ITEM_TYPES.Card].update(getNinjaPrices(CARD_PRICES_URL))
    MARKET_PRICES[ITEM_TYPES.Prophecy].update(getNinjaPrices(PROPHECY_PRICES_URL))
    MARKET_PRICES[ITEM_TYPES.Unique].update(getNinjaPrices(UNIQUE_FLASK_PRICES_URL))
    MARKET_PRICES[ITEM_TYPES.Unique].update(getNinjaPrices(UNIQUE_WEAPON_PRICES_URL))
    MARKET_PRICES[ITEM_TYPES.Unique].update(getNinjaPrices(UNIQUE_ARMOUR_PRICES_URL))
    MARKET_PRICES[ITEM_TYPES.Unique].update(getNinjaPrices(UNIQUE_MAP_PRICES_URL))
    MARKET_PRICES[ITEM_TYPES.Currency].update(getNinjaCurrency(CURRENCY_PRICES_URL))
    MARKET_PRICES[ITEM_TYPES.Currency].update({'Mirror of Kalandra': 650}) #Hardcoded Mirror price

'''
for k,v in MARKET_PRICES[ITEM_TYPES.Currency].items():
    print(str(k) + ': ' + str(v))

for k,v in MARKET_PRICES[ITEM_TYPES.Unique].items():
    print(str(k) + ': ' + str(v))
'''

loadMarketPrices()
splashScreen()

if LOAD_FROM_LOCAL_DUMP_FILE:
    pagefile = 'lastresponse.txt'
    print('Loading page from file ' + pagefile)
    data = loadApiPageFromFile(pagefile)
    stashes = data['stashes']
    findDeals(stashes)
    print("Done!")
else:
    next_change_id = getNinjaNextPageId()
    while(True):
        print('Fetching page #{}...'.format(next_change_id))
        data = getApiPage(next_change_id)
        stashes = data['stashes']
        findDeals(stashes)
        next_change_id = data['next_change_id']
        time.sleep(1)
