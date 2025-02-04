from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
import json
import os
from utils.admin_handler import AdminHandler
from utils.message_manager import MessageManager
from utils.keyboard_manager import KeyboardManager

class ShopBot:
    def __init__(self, token):
        self.token = token
        self.app = Application.builder().token(token).build()
        
        # Charger la configuration
        self.config = self.load_config()
        
        # Charger le catalogue
        self.catalog = self.load_catalog()
        
        # Initialiser les gestionnaires
        self.admin_handler = AdminHandler(self)
        self.message_manager = MessageManager(self)
        self.keyboard_manager = KeyboardManager(self)
        
        # Configuration des handlers
        self.setup_handlers()

    def load_config(self):
        """Charge la configuration depuis config.json"""
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Créer un fichier de configuration par défaut
            config = {
                "admin_ids": [],  # Liste des IDs des administrateurs
                "token": ""  # Token du bot
            }
            with open('config.json', 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4)
            return config

    def load_catalog(self):
        """Charge le catalogue depuis catalog.json"""
        try:
            with open('catalog.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Créer un catalogue vide
            catalog = {
                "categories": [],
                "products": []
            }
            with open('catalog.json', 'w', encoding='utf-8') as f:
                json.dump(catalog, f, indent=4)
            return catalog

    def save_catalog(self):
        """Sauvegarde le catalogue dans catalog.json"""
        with open('catalog.json', 'w', encoding='utf-8') as f:
            json.dump(self.catalog, f, indent=4, ensure_ascii=False)

    def is_admin(self, user_id):
        """Vérifie si un utilisateur est admin"""
        if user_id is None:
            return False
        return str(user_id) in map(str, self.config.get('admin_ids', []))

    def setup_handlers(self):
        """Configure les handlers du bot"""
        self.app.add_handler(CommandHandler("start", self.message_manager.start))
        self.app.add_handler(CommandHandler("admin", self.admin_handler.admin_menu))
        
        # Handler pour les callbacks admin
        self.app.add_handler(CallbackQueryHandler(self.admin_handler.handle_callback, pattern="^(admin|del_|new_prod)"))
        
        # Handler pour les callbacks normaux
        self.app.add_handler(CallbackQueryHandler(self.message_manager.handle_callback))
        
        # Handler pour tous les types de messages texte
        self.app.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.admin_handler.handle_message
        ))
        
        # Handler pour les médias
        self.app.add_handler(MessageHandler(
            filters.PHOTO | filters.VIDEO,
            self.admin_handler.handle_media
        ))

    def run(self):
        """Démarre le bot"""
        print("Le bot démarre...")
        self.app.run_polling()

if __name__ == "__main__":
    # Charger la configuration
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Créer et démarrer le bot
    bot = ShopBot(config['token'])
    bot.run()