import abc
import random
import os
# ANSI escape codes for colors
RED = "\033[31m"
GREEN = "\033[32m"
BLUE = "\033[34m"
RESET = "\033[0m"
MAGENTA = "\033[35m"
YELLOW = "\033[33m"

#Creating classes for characters


class Character(abc.ABC):
    def __init__(self, health, attack):
        self._health = health
        self._attack = attack

    @abc.abstractmethod
    def take_damage(self, damage, attacker=None):
        pass

    @abc.abstractmethod
    def attack(self, other):
        pass

    def is_alive(self):
        return self._health > 0

class Knight(Character):
    def __init__(self, health, attack, shield, armor=True):
        super().__init__(health, attack)
        self._armor = armor
        self._shield = shield
        self._shield_counter = 0

#Knight has passive shield and armor, when shield is active it absorbs 35% of the damage

    def take_damage(self, damage, attacker=None):
        if self._shield_counter > 0 and (not isinstance(attacker, Archer) or (isinstance(attacker, Archer) and not attacker.penetration)):
            damage *= 0.65
            self._shield_counter -= 1

        if self._armor and (not isinstance(attacker, Archer) or (isinstance(attacker, Archer) and not attacker.penetration)):
            damage *= 0.9
        self._health -= damage
        print(f"{RED}Knight takes {damage} damage, health is now {self._health}{RESET}")

    def attack(self, other):
        other.take_damage(self._attack, attacker=self)
        print(f"Knight deals {self._attack} damage")

    def enable_shield(self):
        self._shield_counter = 2
        print(f"{BLUE}Knight's shield is now active for 2 moves{RESET}")

    def status(self):
        shield_status = f"Shield active for {self._shield_counter} more moves" if self._shield_counter > 0 else "Shield inactive"
        print(f"Knight - Health: {self._health}, {shield_status}")

class Wizard(Character):
    def __init__(self, health, attack, fire_shield):
        super().__init__(health, attack)
        self._shield = fire_shield
        self._fire_shield_counter = 0
        self._burning_effects = {}

    def attack(self, other):
        other.take_damage(self._attack, attacker=self)
        self.apply_burning_effect(other)
        print(f"Wizard deals {self._attack} damage and applies burning effect")

#Wizard has a fire shield that reflects 50% of the damage taken back to the attacker

    def take_damage(self, damage, attacker=None):
        if self._fire_shield_counter > 0 and (not isinstance(attacker, Archer) or (isinstance(attacker, Archer) and not attacker.penetration)):
            damage *= 0.8
            if attacker:
                reflected_damage = damage * 0.5
                attacker.take_damage(reflected_damage)
                print(f"Wizard reflects {reflected_damage} damage to the attacker!")
            self._fire_shield_counter -= 1
        self._health -= damage
        print(f"{RED}Wizard takes {damage} damage, health is now {self._health}{RESET}")

    def enable_fire_shield(self):
        self._fire_shield_counter = 3
        print(f"{BLUE}Wizard's fire shield is now active for 3 moves{RESET}")

    def apply_burning_effect(self, target):
        self._burning_effects[target] = 2
    
#Wizard has a passive ability called pyromaniac that heals him for the same amount of damage dealt by the burning effect

    def pyromaniac(self):
        for target, turns_left in list(self._burning_effects.items()):
            if turns_left > 0:
                burn_damage = 40
                heal_amount = burn_damage
                target.take_damage(burn_damage)
                self._health += heal_amount
                print(f"{RED}Burning effect deals {burn_damage} damage to the enemy,{RESET} {GREEN}and heals Wizard for {heal_amount}!{RESET}")
                self._burning_effects[target] -= 1
            if self._burning_effects[target] <= 0:
                del self._burning_effects[target]

    def status(self):
        fire_shield_status = f"Fire shield active for {self._fire_shield_counter} more moves" if self._fire_shield_counter > 0 else "Fire shield inactive"
        burning_status = f"Burning effects on {len(self._burning_effects)} targets"
        print(f"Wizard - Health: {self._health}, {fire_shield_status}, {burning_status}")

class Berserk(Character):
    def __init__(self, health, attack, rage):
        super().__init__(health, attack)
        self.initial_health = health
        self.rage = rage
        self.rage_count = 0
        self.shield_active = False
        self.attack_bonus_applied = False
        self.rage_boost_applied = False

    def attack_bonus(self):
        if self._health < (self.initial_health * 0.4) and not self.attack_bonus_applied:
            self._attack *= 1.4
            self.attack_bonus_applied = True
            print(f"{MAGENTA}Berserk is now enraged with increased attack!{RESET}")

    def attack(self, other):
        self.attack_bonus()
        self.rage_boost()
        other.take_damage(self._attack, attacker=self)
        print(f"Berserk deals {self._attack} damage")
        if self.rage_count > 0:
            self.stop_rage()


#Berserk has a rage ability that boosts his attack by 30% for 3 turns, but he loses 15% of his health when activating it


    def enable_rage(self):
        self.rage_count = 3
        health_loss = self._health * 0.15
        self._health -= health_loss
        print(f"{MAGENTA}Berserk loses {health_loss} health due to rage boost! Current health: {self._health}{RESET}")

    def stop_rage(self):
        self.rage_boost_applied = False
        if not self.rage_boost_applied:
            self._attack /= 1.3
        if self.rage_count > 0:
            self.rage_count -= 1

    def rage_boost(self):
        if self.rage_count > 0 and not self.rage_boost_applied:
            self._attack *= 1.3
            self.rage_boost_applied = True


#Berserk has a shield that absorbs 25% of the damage taken when his health is below 30%

    def activate_shield(self):
        self.shield_active = True
        print(f"{BLUE}Berserk's shield is now active, absorbing 25% damage{RESET}")

    def take_damage(self, damage, attacker=None):
        if self._health < (self.initial_health * 0.3) and not self.shield_active:
            self.activate_shield()
        
        if self.shield_active and (not isinstance(attacker, Archer) or (isinstance(attacker, Archer) and not attacker.penetration)):
            damage *= 0.75

        self._health -= damage
        print(f"{RED}Berserk takes {damage} damage, health is now {self._health}{RESET}")

    def status(self):
        shield_status = "active" if self.shield_active else "inactive"
        print(f"Berserk - Health: {self._health}, Rage count: {self.rage_count}, Shield: {shield_status}")

class Archer(Character):
    def __init__(self, health, attack, penetration=False, agility = False):
        super().__init__(health, attack)
        self.penetration = penetration
        self.penetration_shot_count = 0
        self.agility = agility

#Archer has a passive ability called agility that gives her a 20% chance to dodge an attack

    def agility_chance(self):
        manuever = random.random()
        if manuever > 0.75:
            self.agility = True
        else:
            self.agility = False
            

#Archer has a penetration shot ability that will deal double damage and penetrate through the enemy's armor

    def penetration_shot(self):
        penetration_chance = random.random()
        if self.penetration_shot_count > 0:
            if penetration_chance < 0.5:
                self.penetration = True
                self._attack *= 2
            else:
                self.penetration = False
            self.penetration_shot_count -= 1
        else:
            self.penetration = False

    def attack(self, other):
        original_attack = self._attack
        self.penetration_shot()
        other.take_damage(self._attack, attacker=self)
        if self.penetration:
            print(f"{YELLOW}Archer penetrates through enemy's armor and deals {self._attack} damage!{RESET}")
        else:
            print(f"{RED}Archer deals {self._attack} damage{RESET}")
        if self.penetration:
            self._attack = original_attack

    def take_damage(self, damage, attacker=None):
        self.agility_chance()
        if self.agility == True:
            print(f"{YELLOW} Archer evades the attack!\n Archers current health: {self._health}{RESET}")
        else:
            self._health -= damage
            print(f"{RED}Archer takes {damage} damage! Current health: {self._health}{RESET}")

    def status(self):
        if not self.penetration_shot_count > 0:
            penetration_shot = "Inactive"
        else:
            penetration_shot = self.penetration_shot_count
        print(f"Health: {self._health} penetration shot: {penetration_shot}, Dodging chance: 20%")

    def enable_penetration_shot(self):
        self.penetration_shot_count = 3
        print(f"{YELLOW}Archer will use penetrating arrows for 3 moves!{RESET}")

knight = Knight(health=1000, attack=110, shield=False, armor=True)
wizard = Wizard(health=750, attack=80, fire_shield=False)
berserk = Berserk(health=1100, attack=150, rage=False)
archer = Archer(health=900, attack=100)



print("This is a turn based rpg game called simply 'Battle simulator' we got 4 characters to pick from!\n Knight,Wizard,Berserk and Archer type their name to see their stats!")
print("When finished type 'fight' and choose your character!")

intro = None


def fight():
    pass


def character_introduction(name):
    if name.lower() == "knight":
        return knight
    elif name.lower() == "wizard":
        return wizard
    elif name.lower() == "berserk":
        return berserk
    elif name.lower() == "archer":
        return archer
    elif name.lower() == "fight":
        pass
    else:
        return None
 



base_dir = os.path.dirname(os.path.abspath(__file__))

#Introductory text for each character

while intro is None:
    pick_intro = input("Enter your character: ")  
    intro = pick_intro 

    if intro == "knight":
        try:
            with open(os.path.join(base_dir, 'knight.txt'), 'r') as file:
                print(file.read())
        except FileNotFoundError:
            print(f"File for '{intro}' not found.")
        intro = None
    elif intro == "wizard":
        try:
            with open(os.path.join(base_dir, 'wizard.txt'), 'r') as file:
                print(file.read())
        except FileNotFoundError:
            print(f"File for '{intro}' not found.")
        intro = None
    elif intro == "berserk":
        try:
            with open(os.path.join(base_dir, 'berserk.txt'), 'r') as file:
                print(file.read())
        except FileNotFoundError:
            print(f"File for '{intro}' not found.")
        intro = None
    elif intro == "archer":
        try:
            with open(os.path.join(base_dir, 'archer.txt'), 'r') as file:
                print(file.read())
        except FileNotFoundError:
            print(f"File for '{intro}' not found.")
        intro = None
    elif intro == "fight":
        break
    else:
        print("Unknown character. Please try again.")
        intro = None 

#Choosing characters

def choose_character(name1):
    if name1.lower() == "knight":
        return knight
    elif name1.lower() == "wizard":
        return wizard
    elif name1.lower() == "berserk":
        return berserk
    elif name1.lower() == "archer":
        return archer
    else:
        return None
    

print("Choose your character! (Knight, Wizard, Berserk, Archer)")

player1 = None
player2 = None



while player1 is None:
    player1_name = input("Player 1: ")
    player1 = choose_character(player1_name)
    if player1 is None:
        print("Invalid character. Please choose Knight, Wizard, Berserk, or Archer.")

while player2 is None:
    player2_name = input("Player 2: ")
    player2 = choose_character(player2_name)
    if player2 is None:
        print("Invalid character. Please choose Knight, Wizard, Berserk, or Archer.")
    elif player2_name == player1_name:
        print("Character already taken. Please choose another one.")
        player2 = None

turn = 1 


#Game loop

while player1.is_alive() and player2.is_alive():
    if turn == 1:
        command = input("Player 1 turn! Enter command: ").strip().lower()
        if command == "attack":
            player1.attack(player2)
            if isinstance(player1, Wizard):
                player1.pyromaniac()
            elif isinstance(player1, Berserk):
                player1.rage_boost()
            turn = 2
        elif command == "def":
            if isinstance(player1, Knight):
                player1.enable_shield()
            elif isinstance(player1, Wizard):
                player1.enable_fire_shield()
            elif isinstance(player1, Berserk):
                player1.enable_rage()
            elif isinstance(player1, Archer):
                player1.enable_penetration_shot()
            turn = 2
        elif command == "status":
            player1.status()
        elif command == "exit":
            print("Finishing the game")
            break
        else:
            print("Invalid command. Try again.")
    elif turn == 2:
        command = input("Player 2 turn! Enter command: ").strip().lower()
        if command == "attack":
            player2.attack(player1)
            if isinstance(player2, Wizard):
                player2.pyromaniac()
            elif isinstance(player2, Berserk):
                player2.rage_boost()
            turn = 1
        elif command == "def":
            if isinstance(player2, Knight):
                player2.enable_shield()
            elif isinstance(player2, Wizard):
                player2.enable_fire_shield()
            elif isinstance(player2, Berserk):
                player2.enable_rage()
            elif isinstance(player2, Archer):
                player2.enable_penetration_shot()
            turn = 1
        elif command == "status":
            player2.status()
        elif command == "exit":
            print("Finishing the game")
            break
        else:
            print("Invalid command. Try again.")

print("Game over!")
if player1.is_alive():
    print(f"Player 1 ({player1_name}) wins!")
    while True:
        pass
else:
    print(f"Player 2 ({player2_name}) wins!")
    while True:
        pass
        
        

        

        
        
    
   



    




