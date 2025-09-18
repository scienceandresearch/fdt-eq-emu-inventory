"""
Signet of Might Quest Data Structure
Contains all quest steps, items, and tracking logic for the Aid Grimel quest chain.
"""

class SignetOfMightQuest:
    """Data structure for the complete Signet of Might quest chain."""
    
    def __init__(self):
        self.global_requirements = {
            "elemental_planar_flags": "Elemental Planar Flags (progression)",
            "tradeskills": {
                "blacksmithing": 220,
                "brewing": 220,
                "jewelcrafting": 220,
                "pottery": 220,
                "tailoring": 220,
                "fletching": 220,
                "baking": 220
            }
        }
        
        self.quest_chain = {
            1: self._get_blacksmithing_quest(),
            2: self._get_brewing_quest(),
            3: self._get_jewelcrafting_quest(),
            4: self._get_pottery_quest(),
            5: self._get_tailoring_quest(),
            6: self._get_fletching_quest(),
            7: self._get_baking_quest()
        }
    
    def _get_blacksmithing_quest(self):
        return {
            "name": "Blacksmithing",
            "description": "Create Imbued Breastplate to receive Hardened Leather Signet",
            "key_items": {
                "Drop of Pure Rain": {
                    "quantity": 1,
                    "source": "rare drop, Bastion of Thunder 'vann' mobs",
                    "type": "drop"
                },
                "Sandstorm Pearl": {
                    "quantity": 3,
                    "source": "uncommon, Bastion of Thunder 'jord' mobs",
                    "type": "drop"
                },
                "Storm Rider Blood": {
                    "quantity": 1,
                    "source": "common, Bastion of Thunder 'stormrider' mobs",
                    "type": "drop"
                },
                "Raw Diamond": {
                    "quantity": 2,
                    "source": "random world drop",
                    "type": "drop"
                },
                "Nightmare Mephit Blood": {
                    "quantity": 2,
                    "source": "PoNightmare mephits, common",
                    "type": "drop"
                },
                "Jar of Acid": {
                    "quantity": 1,
                    "source": "vendor: Kanio Paerk, PoK",
                    "type": "vendor"
                },
                "Concentrated Celestial Solvent": {
                    "quantity": 1,
                    "source": "vendor: Darius Gandril, PoK",
                    "type": "vendor"
                },
                "The Scent of Marr": {
                    "quantity": 3,
                    "source": "vendor: Loran Thu'Leth, PoK",
                    "type": "vendor"
                },
                "Mixing Bowl": {
                    "quantity": 1,
                    "source": "vendor: Klen Ironstove, PoK",
                    "type": "vendor"
                }
            },
            "sub_combines": {
                "Celestial Essence": {
                    "quantity": 3,
                    "components": ["Concentrated Celestial Solvent", "The Scent of Marr", "Mixing Bowl"]
                },
                "Acid Wash": {
                    "quantity": 1,
                    "components": ["Jar of Acid"]
                },
                "Powdered Sandstorm Pearl": {
                    "quantity": 1,
                    "components": ["Sandstorm Pearl"]
                },
                "Hurricane Temper": {
                    "quantity": 1,
                    "components": ["Drop of Pure Rain", "Storm Rider Blood"]
                },
                "Black Diamond of Nightmares": {
                    "quantity": 2,
                    "components": ["Raw Diamond", "Nightmare Mephit Blood"],
                    "note": "enchanted Raw Diamond + Mephit Blood"
                }
            },
            "final_combine": {
                "result": "Imbued Breastplate",
                "turn_in_to": "Aid Grimel",
                "reward": "Hardened Leather Signet"
            }
        }
    
    def _get_brewing_quest(self):
        return {
            "name": "Brewing",
            "description": "Create Portable Drink to receive Clay Signet",
            "prerequisite": "Hardened Leather Signet",
            "key_items": {
                "Water Flask": {
                    "quantity": 6,
                    "source": "vendor: Perago Crotal, PoK",
                    "type": "vendor"
                },
                "Kaladim Constitutional": {
                    "quantity": 6,
                    "source": "crafted, Brewing 335",
                    "type": "crafted",
                    "recipe": {
                        "skill": "Brewing",
                        "trivial": 335,
                        "container": "Brewing Barrel",
                        "yields": 1,
                        "components": {
                            "Bottle": {
                                "quantity": 1,
                                "source": "vendor: Bargol Halith, PoK Eastern Trade Building (+70, +240)",
                                "type": "vendor"
                            },
                            "Celestial Essence": {
                                "quantity": 1,
                                "source": "crafted, Baking trivial 15",
                                "type": "crafted",
                                "recipe": {
                                    "skill": "Baking",
                                    "trivial": 15,
                                    "container": "Mixing Bowl",
                                    "yields": 3,
                                    "components": {
                                        "Concentrated Celestial Solvent": {
                                            "quantity": 1,
                                            "source": "vendor: Darius Gandril, PoK Western Trader Building (+55, +1520)",
                                            "type": "vendor"
                                        },
                                        "The Scent of Marr": {
                                            "quantity": 3,
                                            "source": "vendor: Loran Thu'Leth, PoK Western Trader Building (-114, +1415)",
                                            "type": "vendor"
                                        }
                                    }
                                }
                            },
                            "Cork": {
                                "quantity": 1,
                                "source": "vendor: Tabben Bromal, PoK 2nd floor (-382, +536)",
                                "type": "vendor"
                            },
                            "Corking Device": {
                                "quantity": 1,
                                "source": "crafted, Tinkering trivial 174 (always returned)",
                                "type": "crafted",
                                "recipe": {
                                    "skill": "Tinkering",
                                    "trivial": 174,
                                    "container": "Toolbox",
                                    "yields": 1,
                                    "note": "Always returned on success/failure",
                                    "components": {
                                        "Blue Diamond": {
                                            "quantity": 1,
                                            "source": "random world drop",
                                            "type": "drop"
                                        },
                                        "Cogs": {
                                            "quantity": 1,
                                            "source": "vendor: Tabben Bromal, PoK 2nd floor (-382, +536)",
                                            "type": "vendor"
                                        },
                                        "Grease": {
                                            "quantity": 1,
                                            "source": "vendor: Tabben Bromal, PoK 2nd floor (-382, +536)",
                                            "type": "vendor"
                                        },
                                        "Sprockets": {
                                            "quantity": 1,
                                            "source": "vendor: Tabben Bromal, PoK 2nd floor (-382, +536)",
                                            "type": "vendor"
                                        },
                                        "Gears": {
                                            "quantity": 1,
                                            "source": "vendor: Tabben Bromal, PoK 2nd floor (-382, +536)",
                                            "type": "vendor"
                                        },
                                        "Branch of Sylvan Oak": {
                                            "quantity": 1,
                                            "source": "foraged: Eastern Wastes, Wakening Lands",
                                            "type": "foraged"
                                        }
                                    }
                                }
                            },
                            "Fermented Yarrow": {
                                "quantity": 1,
                                "source": "crafted, Brewing trivial 74",
                                "type": "crafted",
                                "recipe": {
                                    "skill": "Brewing",
                                    "trivial": 74,
                                    "container": "Brewing Barrel",
                                    "yields": 6,
                                    "note": "Yields 6, careful not to buy too many Yarrow (26p each)",
                                    "components": {
                                        "Yarrow": {
                                            "quantity": 1,
                                            "source": "vendor: Severg O'Danos, PoK Western Trader Building (-23, +1377)",
                                            "type": "vendor"
                                        },
                                        "Water Flask": {
                                            "quantity": 1,
                                            "source": "vendor: Perago Crotal, PoK Eastern Trade Building (+22, +242)",
                                            "type": "vendor"
                                        }
                                    }
                                }
                            },
                            "Soda Water": {
                                "quantity": 1,
                                "source": "crafted, Brewing trivial 58",
                                "type": "crafted",
                                "recipe": {
                                    "skill": "Brewing",
                                    "trivial": 58,
                                    "container": "Brewing Barrel",
                                    "yields": 1,
                                    "components": {
                                        "Soda": {
                                            "quantity": 1,
                                            "source": "vendor: Klen Ironstove, PoK Eastern Trade Building (-107, +237)",
                                            "type": "vendor"
                                        },
                                        "Water Flask": {
                                            "quantity": 1,
                                            "source": "vendor: Perago Crotal, PoK Eastern Trade Building (+22, +242)",
                                            "type": "vendor"
                                        }
                                    }
                                }
                            },
                            "Strange Dark Fungus": {
                                "quantity": 1,
                                "source": "ground spawn: North Kaladim Farm (patches of ~10, 6min respawn)",
                                "type": "ground_spawn"
                            },
                            "Underfoot Mushroom": {
                                "quantity": 1,
                                "source": "ground spawn: North Kaladim Farm (patches of ~10, 6min respawn)",
                                "type": "ground_spawn"
                            }
                        }
                    }
                },
                "Concentrated Celestial Solvent": {
                    "quantity": 1,
                    "source": "vendor: Darius Gandril, PoK",
                    "type": "vendor"
                },
                "The Scent of Marr": {
                    "quantity": 3,
                    "source": "vendor: Loran Thu'Leth, PoK",
                    "type": "vendor"
                },
                "Mixing Bowl": {
                    "quantity": 1,
                    "source": "vendor: Klen Ironstove, PoK",
                    "type": "vendor"
                }
            },
            "sub_combines": {
                "Celestial Essence": {
                    "quantity": 3,
                    "components": ["Concentrated Celestial Solvent", "The Scent of Marr", "Mixing Bowl"]
                },
                "Purified Water": {
                    "quantity": 3,
                    "components": ["Water Flask"]
                },
                "Twice Brewed Constitutional": {
                    "quantity": 3,
                    "components": ["Kaladim Constitutional"]
                }
            },
            "final_combine": {
                "result": "Portable Drink",
                "additional_component": "Hardened Leather Signet",
                "turn_in_to": "Aid Grimel",
                "reward": "Clay Signet"
            }
        }
    
    def _get_jewelcrafting_quest(self):
        return {
            "name": "Jewelcrafting",
            "description": "Create Velium Blue Diamond Ring to receive Wooden Signet",
            "prerequisite": "Clay Signet",
            "key_items": {
                "Etching Tools": {
                    "quantity": 1,
                    "source": "quest: Meg Tucter, Thurgadin",
                    "type": "quest"
                },
                "Water Flask": {
                    "quantity": 2,
                    "source": "vendor: Perago Crotal, PoK",
                    "type": "vendor"
                },
                "Velium Bar": {
                    "quantity": 5,
                    "source": "vendor: Talem Tucter, Thurgadin; enchant 3 with Enchanter",
                    "type": "vendor",
                    "note": "enchant 3 with Enchanter"
                },
                "Blue Diamond": {
                    "quantity": 1,
                    "source": "random world drop",
                    "type": "drop"
                },
                "Concentrated Celestial Solvent": {
                    "quantity": 1,
                    "source": "vendor: Darius Gandril, PoK",
                    "type": "vendor"
                },
                "The Scent of Marr": {
                    "quantity": 3,
                    "source": "vendor: Loran Thu'Leth, PoK",
                    "type": "vendor"
                },
                "Mixing Bowl": {
                    "quantity": 1,
                    "source": "vendor: Klen Ironstove, PoK",
                    "type": "vendor"
                },
                "Planar's Jewelry Kit": {
                    "quantity": 1,
                    "source": "vendor: Noirin Khalen, PoK",
                    "type": "vendor"
                },
                "Coldain Smithing Hammer": {
                    "quantity": 1,
                    "source": "quest: Coldain Ring #4",
                    "type": "quest"
                },
                "Coldain Velium Temper": {
                    "quantity": 1,
                    "source": "vendor: Nimren Stonecutter, Thurgadin",
                    "type": "vendor"
                }
            },
            "sub_combines": {
                "Celestial Essence": {
                    "quantity": 3,
                    "components": ["Concentrated Celestial Solvent", "The Scent of Marr", "Mixing Bowl"]
                },
                "Purified Water": {
                    "quantity": 1,
                    "components": ["Water Flask"]
                },
                "Mounted Blue Diamond": {
                    "quantity": 1,
                    "components": ["Blue Diamond"]
                },
                "Faceted Blue Diamond": {
                    "quantity": 1,
                    "components": ["Mounted Blue Diamond"]
                },
                "Pure Enchanted Velium Bar": {
                    "quantity": 1,
                    "components": ["Velium Bar", "enchanter spell"]
                }
            },
            "final_combine": {
                "result": "Velium Blue Diamond Ring",
                "additional_component": "Clay Signet",
                "turn_in_to": "Aid Grimel",
                "reward": "Wooden Signet"
            }
        }
    
    def _get_pottery_quest(self):
        return {
            "name": "Pottery",
            "description": "Create Filled Sacred Urn to receive Metal Signet",
            "prerequisite": "Wooden Signet",
            "key_items": {
                # Note: Detailed items list would be extensive, showing key examples
                "Iron Oxide": {
                    "quantity": 1,
                    "source": "drop",
                    "type": "drop"
                },
                "Permafrost Crystals": {
                    "quantity": 1,
                    "source": "drop",
                    "type": "drop"
                },
                "Sacred Water": {
                    "quantity": 1,
                    "source": "drop",
                    "type": "drop"
                }
            },
            "sub_combines": {
                "Unfired Ceramic Lining": {
                    "quantity": 1,
                    "components": ["various pottery components"]
                },
                "Ceramic Lining": {
                    "quantity": 1,
                    "components": ["Unfired Ceramic Lining"]
                },
                "Lacquered Opal": {
                    "quantity": 3,
                    "components": ["opal", "lacquer"]
                },
                "Large Block of Magic Clay": {
                    "quantity": 3,
                    "components": ["clay", "enchanter spell"],
                    "note": "enchanted"
                },
                "Vial of Purified Mana": {
                    "quantity": 1,
                    "components": ["mana components"]
                },
                "Unfired Sacred Urn": {
                    "quantity": 1,
                    "components": ["pottery components"]
                },
                "Sacred Urn": {
                    "quantity": 1,
                    "components": ["Unfired Sacred Urn"]
                },
                "Filled Sacred Urn": {
                    "quantity": 1,
                    "components": ["Sacred Urn", "Sacred Water"]
                }
            },
            "final_combine": {
                "result": "Filled Sacred Urn",
                "additional_component": "Wooden Signet",
                "turn_in_to": "Aid Grimel",
                "reward": "Metal Signet"
            }
        }
    
    def _get_tailoring_quest(self):
        return {
            "name": "Tailoring",
            "description": "Create Fire Undergarment Tunic to receive Marked Signet",
            "prerequisite": "Metal Signet",
            "key_items": {
                "Fire Mephit Blood": {
                    "quantity": 1,
                    "source": "drop",
                    "type": "drop"
                },
                "Molten Ore": {
                    "quantity": 1,
                    "source": "drop",
                    "type": "drop"
                },
                "Obsidianwood Sap": {
                    "quantity": 1,
                    "source": "drop",
                    "type": "drop"
                },
                "Fire Arachnid Silk": {
                    "quantity": 1,
                    "source": "drop",
                    "type": "drop"
                }
            },
            "sub_combines": {
                "Vial of Purified Mana": {
                    "quantity": 3,
                    "components": ["mana components"]
                },
                "Firestrand Curing Agent": {
                    "quantity": 1,
                    "components": ["fire components"]
                },
                "Firesilk Swatch": {
                    "quantity": 3,
                    "components": ["Fire Arachnid Silk"]
                },
                "Red Diamond of Fire": {
                    "quantity": 1,
                    "components": ["diamond", "enchanter imbue"]
                },
                "Enchanted Molten Bar": {
                    "quantity": 1,
                    "components": ["Molten Ore", "enchanter spell"]
                },
                "Emblem of Fire": {
                    "quantity": 1,
                    "components": ["fire components"]
                }
            },
            "final_combine": {
                "result": "Fire Undergarment Tunic",
                "additional_component": "Metal Signet",
                "turn_in_to": "Aid Grimel",
                "reward": "Marked Signet"
            }
        }
    
    def _get_fletching_quest(self):
        return {
            "name": "Fletching",
            "description": "Create Signet Featherwood Bow to receive Runed Signet",
            "prerequisite": "Marked Signet",
            "key_items": {
                "Featherwood Bowstave": {
                    "quantity": 1,
                    "source": "drop, Plane of Air",
                    "type": "drop"
                },
                "Planing Tool": {
                    "quantity": 1,
                    "source": "vendor: Ellis Cloudchaser, PoK",
                    "type": "vendor"
                },
                "Air Arachnid Silk": {
                    "quantity": 2,
                    "source": "drop, Plane of Air spiders",
                    "type": "drop"
                },
                "Clump of Wax": {
                    "quantity": 1,
                    "source": "vendor: Ellis Cloudchaser, PoK",
                    "type": "vendor"
                },
                "Wind Metal Bow Cam": {
                    "quantity": 2,
                    "source": "tinkered, trivial 282",
                    "type": "crafted",
                    "recipe": {
                        "skill": "Tinkering",
                        "trivial": 282,
                        "container": "Toolbox",
                        "yields": 1,
                        "note": "Recipe is the same for all four Bow Cams. Only difference is the elemental drop.",
                        "components": {
                            "Wind Metal Gears": {
                                "quantity": 1,
                                "source": "crafted, Blacksmithing trivial 102",
                                "type": "crafted",
                                "recipe": {
                                    "skill": "Blacksmithing",
                                    "trivial": 102,
                                    "container": "Forge",
                                    "yields": 1,
                                    "note": "Also returns Wind Metal Bolts",
                                    "components": {
                                        "Cam Parts Mold": {
                                            "quantity": 1,
                                            "source": "vendor: Ellis Cloudchaser, PoK Western Trader Building (-120, +1470)",
                                            "type": "vendor"
                                        },
                                        "Chunk of Wind Metal": {
                                            "quantity": 1,
                                            "source": "drop: Elemental Planes (Air)",
                                            "type": "drop",
                                            "note": "Dropped from Elemental Planes trash"
                                        }
                                    }
                                }
                            },
                            "Wind Metal Bolts": {
                                "quantity": 1,
                                "source": "crafted, see Wind Metal Gears",
                                "type": "crafted",
                                "note": "Will be given upon combine of Wind Metal Gears"
                            },
                            "Jar of Clockwork Grease": {
                                "quantity": 1,
                                "source": "crafted, Tinkering trivial 15",
                                "type": "crafted",
                                "recipe": {
                                    "skill": "Tinkering",
                                    "trivial": 15,
                                    "container": "Toolbox",
                                    "yields": 1,
                                    "note": "No Fail recipe",
                                    "components": {
                                        "Clockwork Grease": {
                                            "quantity": 2,
                                            "source": "foraged: Plane of Innovation",
                                            "type": "foraged"
                                        },
                                        "Small Grease Jar": {
                                            "quantity": 1,
                                            "source": "crafted, Pottery trivial 17",
                                            "type": "crafted",
                                            "recipe": {
                                                "skill": "Pottery",
                                                "trivial": 17,
                                                "container": "Kiln",
                                                "yields": 1,
                                                "components": {
                                                    "Quality Firing Sheet": {
                                                        "quantity": 1,
                                                        "source": "vendor: Elisha Dirtyshoes, PoK Northern Trader Building (+400, +950)",
                                                        "type": "vendor"
                                                    },
                                                    "Unfired Small Grease Jar": {
                                                        "quantity": 1,
                                                        "source": "crafted, Pottery trivial 31",
                                                        "type": "crafted",
                                                        "recipe": {
                                                            "skill": "Pottery",
                                                            "trivial": 31,
                                                            "container": "Pottery Wheel",
                                                            "yields": 1,
                                                            "components": {
                                                                "Water Flask": {
                                                                    "quantity": 1,
                                                                    "source": "vendor: Perago Crotal, PoK Eastern Trader Building (+16, +238)",
                                                                    "type": "vendor"
                                                                },
                                                                "Block of Clay": {
                                                                    "quantity": 1,
                                                                    "source": "vendor: Elisha Dirtyshoes, PoK Northern Trader Building (+400, +950)",
                                                                    "type": "vendor"
                                                                },
                                                                "Small Grease Jar Sketch": {
                                                                    "quantity": 1,
                                                                    "source": "vendor: Elisha Dirtyshoes, PoK Northern Trader Building (+400, +950)",
                                                                    "type": "vendor"
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            },
                            "File": {
                                "quantity": 1,
                                "source": "crafted, Blacksmithing trivial 21",
                                "type": "crafted",
                                "recipe": {
                                    "skill": "Blacksmithing",
                                    "trivial": 21,
                                    "container": "Forge",
                                    "yields": 1,
                                    "note": "Returns on Combine",
                                    "components": {
                                        "Water Flask": {
                                            "quantity": 1,
                                            "source": "vendor: Borik Darkanvil, PoK Southeast Trader Building (-375, +500)",
                                            "type": "vendor"
                                        },
                                        "File Mold": {
                                            "quantity": 1,
                                            "source": "vendor: Borik Darkanvil, PoK Southeast Trader Building (-375, +500)",
                                            "type": "vendor"
                                        },
                                        "Metal Bits": {
                                            "quantity": 1,
                                            "source": "crafted, Blacksmithing trivial 18",
                                            "type": "crafted",
                                            "recipe": {
                                                "skill": "Blacksmithing",
                                                "trivial": 18,
                                                "container": "Forge",
                                                "yields": 2,
                                                "components": {
                                                    "Small Piece of Ore": {
                                                        "quantity": 2,
                                                        "source": "vendor: Borik Darkanvil, PoK Southeast Trader Building (-375, +500)",
                                                        "type": "vendor"
                                                    },
                                                    "Water Flask": {
                                                        "quantity": 1,
                                                        "source": "vendor: Perago Crotal, PoK Eastern Trader Building (+16, +238)",
                                                        "type": "vendor"
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            },
            "sub_combines": {
                "Air Arachnid Silk String": {
                    "quantity": 1,
                    "components": ["Air Arachnid Silk"]
                },
                "Signet Featherwood Bow": {
                    "quantity": 1,
                    "components": ["Featherwood Bowstave", "Air Arachnid Silk String", "Wind Metal Bow Cam"]
                }
            },
            "final_combine": {
                "result": "Signet Featherwood Bow",
                "additional_component": "Marked Signet",
                "turn_in_to": "Aid Grimel",
                "reward": "Runed Signet"
            }
        }
    
    def _get_baking_quest(self):
        return {
            "name": "Baking + Final Turn-In",
            "description": "Create Food Satchel and complete final turn-ins for Signet of Might",
            "prerequisite": "Runed Signet",
            "key_items": {
                "Bristlebane's Party Platter": {
                    "quantity": 3,
                    "source": "Baking 322; many sub-recipes",
                    "type": "crafted",
                    "recipe": {
                        "skill": "Baking",
                        "trivial": 322,
                        "container": "Oven",
                        "yields": 2,
                        "note": "Master Recipe - Creates 2 Party Platters per combine",
                        "components": {
                            "Bucket of Crab Legs": {
                                "quantity": 1,
                                "source": "crafted, Baking",
                                "type": "crafted",
                                "recipe": {
                                    "skill": "Baking",
                                    "trivial": 135,
                                    "container": "Oven",
                                    "yields": 2,
                                    "components": {
                                        "Bucket": {
                                            "quantity": 1,
                                            "source": "crafted (returned on fail/success)",
                                            "type": "crafted",
                                            "note": "Returned on fail/success"
                                        },
                                        "Butter": {
                                            "quantity": 1,
                                            "source": "crafted or vendor",
                                            "type": "vendor"
                                        },
                                        "Cracked Regrua Meat": {
                                            "quantity": 1,
                                            "source": "crafted",
                                            "type": "crafted"
                                        },
                                        "Spices": {
                                            "quantity": 1,
                                            "source": "vendor",
                                            "type": "vendor"
                                        }
                                    }
                                }
                            },
                            "Hero Sandwich": {
                                "quantity": 1,
                                "source": "crafted, Baking",
                                "type": "crafted",
                                "recipe": {
                                    "skill": "Baking",
                                    "trivial": 162,
                                    "container": "Oven",
                                    "yields": 2,
                                    "components": {
                                        "Dressing": {
                                            "quantity": 1,
                                            "source": "crafted",
                                            "type": "crafted"
                                        },
                                        "Hero Parts": {
                                            "quantity": 1,
                                            "source": "drop",
                                            "type": "drop"
                                        },
                                        "Loaf of Bread": {
                                            "quantity": 1,
                                            "source": "crafted, vendor, quest, or drop",
                                            "type": "vendor"
                                        },
                                        "Smoked Hero Parts": {
                                            "quantity": 1,
                                            "source": "crafted",
                                            "type": "crafted"
                                        },
                                        "Spiced Hero Parts": {
                                            "quantity": 1,
                                            "source": "crafted",
                                            "type": "crafted"
                                        },
                                        "Vegetables": {
                                            "quantity": 1,
                                            "source": "foraged, crafted, or vendor",
                                            "type": "foraged"
                                        }
                                    }
                                }
                            },
                            "Picnic Basket": {
                                "quantity": 1,
                                "source": "crafted, Tailoring",
                                "type": "crafted",
                                "recipe": {
                                    "skill": "Tailoring",
                                    "trivial": 188,
                                    "container": "Loom",
                                    "yields": 10,
                                    "note": "Creates 10 Picnic Baskets per combine",
                                    "components": {
                                        "Steel Boning": {
                                            "quantity": 1,
                                            "source": "crafted",
                                            "type": "crafted"
                                        },
                                        "Woven Mandrake": {
                                            "quantity": 1,
                                            "source": "crafted",
                                            "type": "crafted"
                                        }
                                    }
                                }
                            },
                            "Planar Fruit Pie": {
                                "quantity": 2,
                                "source": "crafted, Baking",
                                "type": "crafted",
                                "recipe": {
                                    "skill": "Baking",
                                    "trivial": 188,
                                    "container": "Oven",
                                    "yields": 1,
                                    "components": {
                                        "Celestial Essence": {
                                            "quantity": 2,
                                            "source": "crafted, Baking trivial 15",
                                            "type": "crafted",
                                            "recipe": {
                                                "skill": "Baking",
                                                "trivial": 15,
                                                "container": "Mixing Bowl",
                                                "yields": 3,
                                                "components": {
                                                    "Concentrated Celestial Solvent": {
                                                        "quantity": 1,
                                                        "source": "vendor: Darius Gandril, PoK Western Trader Building (+55, +1520)",
                                                        "type": "vendor"
                                                    },
                                                    "The Scent of Marr": {
                                                        "quantity": 3,
                                                        "source": "vendor: Loran Thu'Leth, PoK Western Trader Building (-114, +1415)",
                                                        "type": "vendor"
                                                    }
                                                }
                                            }
                                        },
                                        "Clump of Dough": {
                                            "quantity": 1,
                                            "source": "crafted",
                                            "type": "crafted"
                                        },
                                        "Frosting": {
                                            "quantity": 1,
                                            "source": "vendor",
                                            "type": "vendor"
                                        },
                                        "Muffin Tin": {
                                            "quantity": 1,
                                            "source": "crafted (returned on fail/success)",
                                            "type": "crafted",
                                            "note": "Returned on fail/success"
                                        },
                                        "Planar Fruit": {
                                            "quantity": 1,
                                            "source": "foraged",
                                            "type": "foraged"
                                        }
                                    }
                                }
                            },
                            "Slarghilug Stuffed Poppers": {
                                "quantity": 1,
                                "source": "crafted, Baking",
                                "type": "crafted",
                                "recipe": {
                                    "skill": "Baking",
                                    "trivial": 188,
                                    "container": "Oven",
                                    "yields": 2,
                                    "components": {
                                        "Bottle of Milk": {
                                            "quantity": 1,
                                            "source": "vendor or drop",
                                            "type": "vendor"
                                        },
                                        "Cup of Flour": {
                                            "quantity": 1,
                                            "source": "vendor",
                                            "type": "vendor"
                                        },
                                        "Habanero Pepper": {
                                            "quantity": 1,
                                            "source": "foraged",
                                            "type": "foraged"
                                        },
                                        "Mature Cheese": {
                                            "quantity": 1,
                                            "source": "crafted",
                                            "type": "crafted"
                                        },
                                        "Non-Stick Frying Pan": {
                                            "quantity": 1,
                                            "source": "crafted (returned on fail/success)",
                                            "type": "crafted",
                                            "note": "Returned on fail/success"
                                        },
                                        "Slarghilug Leg": {
                                            "quantity": 1,
                                            "source": "drop",
                                            "type": "drop"
                                        }
                                    }
                                }
                            }
                        }
                    }
                },
                "Hope Stone": {
                    "quantity": 1,
                    "source": "rare random drop, Elemental Planes",
                    "type": "drop"
                }
            },
            "sub_combines": {
                "Food Satchel": {
                    "quantity": 1,
                    "components": ["Bristlebane's Party Platter", "Bristlebane's Party Platter", "Bristlebane's Party Platter", "Runed Signet"]
                }
            },
            "final_combines": [
                {
                    "result": "Marked Runed Signet",
                    "components": ["Food Satchel"],
                    "turn_in_to": "Aid Grimel"
                },
                {
                    "result": "Signet of the Arcane (or swap for Signet of Might)",
                    "components": ["Hope Stone", "Marked Runed Signet"],
                    "turn_in_to": "Councilman Taldarius"
                }
            ]
        }
    
    def get_all_unique_items(self):
        """Get a list of all unique items needed across all quests."""
        all_items = {}
        
        for quest_num, quest_data in self.quest_chain.items():
            # Add key items
            for item_name, item_data in quest_data.get("key_items", {}).items():
                if item_name not in all_items:
                    all_items[item_name] = {
                        "total_quantity": 0,
                        "sources": set(),
                        "used_in_quests": []
                    }
                all_items[item_name]["total_quantity"] += item_data["quantity"]
                all_items[item_name]["sources"].add(item_data["source"])
                all_items[item_name]["used_in_quests"].append(quest_data["name"])
        
        return all_items
    
    def get_quest_progress_summary(self, inventory_items):
        """Analyze inventory and return progress summary for all quests."""
        progress = {}
        
        for quest_num, quest_data in self.quest_chain.items():
            quest_name = quest_data["name"]
            progress[quest_name] = self._analyze_quest_progress(quest_data, inventory_items)
        
        return progress
    
    def _analyze_quest_progress(self, quest_data, inventory_items):
        """Analyze progress for a single quest."""
        key_items = quest_data.get("key_items", {})
        owned_items = {}
        missing_items = {}
        
        for item_name, item_info in key_items.items():
            required_qty = item_info["quantity"]
            owned_qty = self._count_item_in_inventory(item_name, inventory_items)
            
            owned_items[item_name] = {
                "owned": owned_qty,
                "required": required_qty,
                "satisfied": owned_qty >= required_qty,
                "source": item_info["source"],
                "type": item_info["type"]
            }
            
            if owned_qty < required_qty:
                missing_items[item_name] = {
                    "needed": required_qty - owned_qty,
                    "source": item_info["source"],
                    "type": item_info["type"]
                }
        
        total_items = len(key_items)
        satisfied_items = len([item for item in owned_items.values() if item["satisfied"]])
        
        return {
            "owned_items": owned_items,
            "missing_items": missing_items,
            "progress_percentage": (satisfied_items / total_items * 100) if total_items > 0 else 0,
            "items_satisfied": satisfied_items,
            "total_items": total_items,
            "can_complete": len(missing_items) == 0
        }
    
    def _count_item_in_inventory(self, item_name, inventory_items):
        """Count how many of a specific item exist in inventory."""
        if inventory_items is None or inventory_items.empty:
            return 0
        
        # Search for exact matches and partial matches
        exact_matches = inventory_items[
            (inventory_items['Name'].str.lower() == item_name.lower()) &
            (inventory_items['IsEmpty'] == False)
        ]
        
        if not exact_matches.empty:
            return exact_matches['Count'].astype(int).sum()
        
        # Try partial match for items with variations
        partial_matches = inventory_items[
            (inventory_items['Name'].str.contains(item_name, case=False, na=False)) &
            (inventory_items['IsEmpty'] == False)
        ]
        
        if not partial_matches.empty:
            return partial_matches['Count'].astype(int).sum()
        
        return 0
