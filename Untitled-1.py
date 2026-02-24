"""
Elite Neural Evolve v8.0 - Android Native Application
Application APK native pour Android avec Kivy

Installation:
1. Installer buildozer: pip install buildozer cython
2. Compiler: buildozer android debug
3. L'APK sera dans bin/

Auteur: Elite AI Team
Version: 8.0.0
"""

import kivy
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.uix.slider import Slider
from kivy.graphics import Color, RoundedRectangle
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.utils import get_color_from_hex

import json
import os
import random
from datetime import datetime

# Configuration Kivy
kivy.require('2.2.0')

# =============================================================================
# COULEURS DU THÈME
# =============================================================================
COLORS = {
    'primary': '#1a5f7a',
    'secondary': '#2d6a4f',
    'accent': '#ffc107',
    'danger': '#dc3545',
    'success': '#28a745',
    'dark': '#0e1117',
    'darker': '#1a1d24',
    'light': '#ffffff',
    'gray': '#6c757d',
    'text': '#e9ecef'
}

# =============================================================================
# GESTIONNAIRE DE DONNÉES
# =============================================================================
class DataManager:
    """Gestionnaire centralisé des données."""
    
    def __init__(self):
        self.data_dir = self._get_data_dir()
        self.brain_file = os.path.join(self.data_dir, 'neural_memory.json')
        self.bankroll_file = os.path.join(self.data_dir, 'bankroll.json')
        self.settings_file = os.path.join(self.data_dir, 'settings.json')
        
        self._ensure_data_dir()
        self.brain = self._load_brain()
        self.bankroll = self._load_bankroll()
        self.settings = self._load_settings()
    
    def _get_data_dir(self):
        try:
            from android.storage import primary_external_storage_path
            return os.path.join(primary_external_storage_path(), 'EliteNeural')
        except:
            return os.path.expanduser('~/.elite_neural')
    
    def _ensure_data_dir(self):
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _load_brain(self):
        default = {
            'weights': {'Forme': 0.25, 'H2H': 0.20, 'Attaque': 0.15,
                       'Défense': 0.15, 'Domicile': 0.10, 'xG': 0.15},
            'velocity': {},
            'history': [],
            'total_cycles': 0,
            'accuracy': 0.0
        }
        return self._load_json(self.brain_file, default)
    
    def _load_bankroll(self):
        default = {
            'initial_balance': 0.0, 'current_balance': 0.0,
            'total_wagered': 0.0, 'total_won': 0.0, 'total_lost': 0.0,
            'transactions': [], 'roi': 0.0, 'win_rate': 0.0, 'total_bets': 0
        }
        return self._load_json(self.bankroll_file, default)
    
    def _load_settings(self):
        default = {
            'api_key': '', 'learning_rate': 0.05,
            'kelly_fraction': 0.25, 'notifications': True, 'theme': 'dark'
        }
        return self._load_json(self.settings_file, default)
    
    def _load_json(self, filepath, default):
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except: pass
        return default
    
    def _save_json(self, filepath, data):
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except: return False
    
    def save_brain(self): return self._save_json(self.brain_file, self.brain)
    def save_bankroll(self): return self._save_json(self.bankroll_file, self.bankroll)
    def save_settings(self): return self._save_json(self.settings_file, self.settings)

# Instance globale
data_manager = DataManager()

# =============================================================================
# MOTEUR DE PRÉDICTION
# =============================================================================
class PredictionEngine:
    """Moteur de calcul des prédictions."""
    
    @staticmethod
    def get_mock_data(home, away):
        return {
            'home': {
                'name': home, 'form_score': random.uniform(0.4, 0.85),
                'goals_scored': random.randint(20, 60),
                'goals_conceded': random.randint(15, 40),
                'xg': random.uniform(1.2, 2.5)
            },
            'away': {
                'name': away, 'form_score': random.uniform(0.3, 0.75),
                'goals_scored': random.randint(15, 50),
                'goals_conceded': random.randint(18, 45),
                'xg': random.uniform(1.0, 2.0)
            },
            'h2h': {
                'total': random.randint(5, 20),
                'home_wins': random.randint(2, 10)
            }
        }
    
    @staticmethod
    def calculate_probability(match_data, weights):
        home = match_data['home']
        away = match_data['away']
        h2h = match_data['h2h']
        
        factors = {
            'Forme': home['form_score'] * weights['Forme'],
            'H2H': (h2h['home_wins'] / max(h2h['total'], 1)) * weights['H2H'],
            'Attaque': (home['goals_scored'] / max(home['goals_scored'] + away['goals_scored'], 1)) * weights['Attaque'],
            'Défense': (1 - home['goals_conceded'] / max(home['goals_conceded'] + away['goals_conceded'], 1)) * weights['Défense'],
            'Domicile': 0.05 * weights['Domicile'],
            'xG': (home['xg'] / max(home['xg'] + away['xg'], 1)) * weights['xG']
        }
        
        prob = max(0.05, min(0.95, sum(factors.values())))
        return prob, factors
    
    @staticmethod
    def calculate_ev(probability, odds):
        return (probability * odds) - 1
    
    @staticmethod
    def calculate_kelly(probability, odds, fraction=0.25):
        if odds <= 1: return 0
        q = 1 - probability
        b = odds - 1
        kelly = max(0, (probability * b - q) / b) * fraction
        return min(kelly, 0.25)

# =============================================================================
# MOTEUR D'APPRENTISSAGE
# =============================================================================
class LearningEngine:
    @staticmethod
    def update_weights(brain, success, factors):
        lr = data_manager.settings.get('learning_rate', 0.05)
        momentum = 0.9
        
        new_weights = brain['weights'].copy()
        new_velocity = brain.get('velocity', {}).copy()
        
        for factor in factors:
            if factor not in new_weights: continue
            current = new_weights[factor]
            vel = new_velocity.get(factor, 0)
            gradient = lr * (1 - current) if success else -lr * current
            new_velocity[factor] = momentum * vel + gradient
            new_weights[factor] = max(0.01, current + new_velocity[factor])
        
        total = sum(new_weights.values())
        if total > 0:
            new_weights = {k: round(v / total, 4) for k, v in new_weights.items()}
        
        return new_weights, new_velocity

# =============================================================================
# COMPOSANT UI: CARTE MÉTRIQUE
# =============================================================================
class MetricCard(BoxLayout):
    def __init__(self, title='', value='', delta='', **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = dp(80)
        self.padding = dp(10)
        self.spacing = dp(5)
        
        with self.canvas.before:
            Color(*get_color_from_hex(COLORS['darker']))
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(10)])
        
        self.add_widget(Label(text=title, font_size=dp(12),
                             color=get_color_from_hex(COLORS['gray']), size_hint_y=0.3))
        self.add_widget(Label(text=str(value), font_size=dp(24), bold=True,
                             color=get_color_from_hex(COLORS['light']), size_hint_y=0.5))
        if delta:
            delta_color = COLORS['success'] if '+' in delta or 'VALUE' in delta else COLORS['danger']
            self.add_widget(Label(text=delta, font_size=dp(10),
                                 color=get_color_from_hex(delta_color), size_hint_y=0.2))
    
    def on_size(self, *args):
        if hasattr(self, 'rect'):
            self.rect.pos, self.rect.size = self.pos, self.size

# =============================================================================
# ÉCRAN ACCUEIL
# =============================================================================
class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))
        
        with layout.canvas.before:
            Color(*get_color_from_hex(COLORS['dark']))
            self.bg = RoundedRectangle(pos=layout.pos, size=layout.size)
        
        # Header
        header = BoxLayout(size_hint_y=0.15)
        header.add_widget(Label(text='🛡️ ELITE NEURAL', font_size=dp(28), bold=True,
                               color=get_color_from_hex(COLORS['primary'])))
        layout.add_widget(header)
        
        # Stats
        stats = GridLayout(cols=2, spacing=dp(10), size_hint_y=0.25)
        bankroll, brain = data_manager.bankroll, data_manager.brain
        stats.add_widget(MetricCard('💰 Bankroll', f"{bankroll['current_balance']:.2f}€"))
        stats.add_widget(MetricCard('🎯 Précision', f"{brain['accuracy']*100:.1f}%"))
        stats.add_widget(MetricCard('📈 ROI', f"{bankroll['roi']:.1f}%"))
        stats.add_widget(MetricCard('🎰 Paris', str(bankroll['total_bets'])))
        layout.add_widget(stats)
        
        # Boutons
        buttons = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=0.4)
        for text, screen, color in [
            ('🔍 Nouvelle Analyse', 'scanner', COLORS['primary']),
            ('💰 Gérer Bankroll', 'bankroll', COLORS['secondary']),
            ('📊 Statistiques', 'stats', COLORS['accent']),
            ('⚙️ Paramètres', 'settings', COLORS['gray'])
        ]:
            btn = Button(text=text, font_size=dp(18), size_hint_y=None, height=dp(60),
                        background_normal='', background_color=get_color_from_hex(color))
            btn.bind(on_press=lambda x, s=screen: setattr(self.manager, 'current', s))
            buttons.add_widget(btn)
        layout.add_widget(buttons)
        
        # Footer
        layout.add_widget(Label(text=f'v8.0.0 • {datetime.now().strftime("%d/%m/%Y")}',
                               font_size=dp(12), color=get_color_from_hex(COLORS['gray']), size_hint_y=0.1))
        
        self.add_widget(layout)

# =============================================================================
# ÉCRAN SCANNER
# =============================================================================
class ScannerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_prediction = None
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        with layout.canvas.before:
            Color(*get_color_from_hex(COLORS['dark']))
            self.bg = RoundedRectangle(pos=layout.pos, size=layout.size)
        
        # Header
        header = BoxLayout(size_hint_y=0.1)
        back = Button(text='← Retour', font_size=dp(16), size_hint_x=0.3,
                     background_normal='', background_color=get_color_from_hex(COLORS['darker']))
        back.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        header.add_widget(back)
        header.add_widget(Label(text='🔍 Analyse de Match', font_size=dp(20), bold=True,
                               color=get_color_from_hex(COLORS['primary'])))
        layout.add_widget(header)
        
        # Form
        form = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=0.25)
        
        teams = BoxLayout(spacing=dp(10))
        self.home_input = TextInput(text='Marseille', multiline=False, font_size=dp(16), size_hint_x=0.5)
        self.away_input = TextInput(text='Lyon', multiline=False, font_size=dp(16), size_hint_x=0.5)
        teams.add_widget(self.home_input)
        teams.add_widget(self.away_input)
        form.add_widget(teams)
        
        odds_row = BoxLayout(spacing=dp(10))
        odds_row.add_widget(Label(text='Cote:', font_size=dp(16),
                                 color=get_color_from_hex(COLORS['text']), size_hint_x=0.5))
        self.odds_input = TextInput(text='2.00', input_filter='float', multiline=False,
                                   font_size=dp(18), size_hint_x=0.3)
        odds_row.add_widget(self.odds_input)
        form.add_widget(odds_row)
        layout.add_widget(form)
        
        # Bouton analyse
        self.analyze_btn = Button(text='🚀 LANCER L\'ANALYSE', font_size=dp(20), bold=True,
                                 size_hint_y=0.12, background_normal='',
                                 background_color=get_color_from_hex(COLORS['primary']))
        self.analyze_btn.bind(on_press=self.analyze)
        layout.add_widget(self.analyze_btn)
        
        # Résultats
        self.results = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=0.5)
        self.results.add_widget(Label(text='Lancez une analyse...', font_size=dp(14),
                                     color=get_color_from_hex(COLORS['gray'])))
        layout.add_widget(self.results)
        
        self.add_widget(layout)
    
    def analyze(self, instance):
        home, away = self.home_input.text.strip(), self.away_input.text.strip()
        if len(home) < 2 or len(away) < 2: return
        
        try: odds = float(self.odds_input.text)
        except: return
        
        self.analyze_btn.text, self.analyze_btn.disabled = '⏳ Analyse...', True
        Clock.schedule_once(lambda dt: self._perform_analysis(home, away, odds), 1.5)
    
    def _perform_analysis(self, home, away, odds):
        match_data = PredictionEngine.get_mock_data(home, away)
        brain = data_manager.brain
        prob, factors = PredictionEngine.calculate_probability(match_data, brain['weights'])
        ev = PredictionEngine.calculate_ev(prob, odds)
        kelly = PredictionEngine.calculate_kelly(prob, odds, data_manager.settings.get('kelly_fraction', 0.25))
        stake = kelly * data_manager.bankroll['current_balance']
        
        self.current_prediction = {
            'home': home, 'away': away, 'odds': odds, 'probability': prob,
            'ev': ev, 'kelly': kelly, 'stake': stake, 'factors': factors, 'match_data': match_data,
            'timestamp': datetime.now().isoformat()
        }
        
        self._show_results()
        self.analyze_btn.text, self.analyze_btn.disabled = '🚀 LANCER L\'ANALYSE', False
    
    def _show_results(self):
        self.results.clear_widgets()
        pred = self.current_prediction
        
        # Métriques
        metrics = GridLayout(cols=2, spacing=dp(8), size_hint_y=0.4)
        metrics.add_widget(MetricCard('📊 Probabilité', f"{pred['probability']*100:.1f}%"))
        metrics.add_widget(MetricCard('💰 EV', f"{pred['ev']*100:.1f}%", 'VALUE' if pred['ev'] > 0 else 'NO VALUE'))
        metrics.add_widget(MetricCard('🎯 Mise Kelly', f"{pred['stake']:.2f}€"))
        metrics.add_widget(MetricCard('📈 Confiance', f"{pred['probability']*pred['odds']:.2f}"))
        self.results.add_widget(metrics)
        
        # Facteurs
        self.results.add_widget(Label(text='─── Facteurs ───', font_size=dp(14),
                                     color=get_color_from_hex(COLORS['gray']), size_hint_y=0.1))
        
        factors_box = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=0.35)
        for factor, value in pred['factors'].items():
            row = BoxLayout(spacing=dp(5))
            row.add_widget(Label(text=factor, font_size=dp(12),
                                color=get_color_from_hex(COLORS['text']), size_hint_x=0.3))
            row.add_widget(ProgressBar(value=abs(value)*100, max=100, size_hint_x=0.7))
            factors_box.add_widget(row)
        self.results.add_widget(factors_box)
        
        # Signal
        signal = f"🎯 SIGNAL FORT: {pred['home']}" if pred['ev'] > 0.15 else \
                 (f"💡 Signal modéré: {pred['home']}" if pred['ev'] > 0 else "⚠️ Pas de value")
        signal_color = COLORS['success'] if pred['ev'] > 0.15 else (COLORS['accent'] if pred['ev'] > 0 else COLORS['danger'])
        self.results.add_widget(Label(text=signal, font_size=dp(16), bold=True,
                                     color=get_color_from_hex(signal_color), size_hint_y=0.15))
        
        # Bouton apprentissage
        learn = Button(text='🧠 Aller à l\'apprentissage', font_size=dp(14),
                      background_normal='', background_color=get_color_from_hex(COLORS['secondary']))
        learn.bind(on_press=lambda x: setattr(self.manager, 'current', 'learning'))
        self.results.add_widget(learn)

# =============================================================================
# ÉCRAN BANKROLL
# =============================================================================
class BankrollScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        with layout.canvas.before:
            Color(*get_color_from_hex(COLORS['dark']))
            self.bg = RoundedRectangle(pos=layout.pos, size=layout.size)
        
        # Header
        header = BoxLayout(size_hint_y=0.1)
        back = Button(text='← Retour', font_size=dp(16), size_hint_x=0.3,
                     background_normal='', background_color=get_color_from_hex(COLORS['darker']))
        back.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        header.add_widget(back)
        header.add_widget(Label(text='💰 Bankroll', font_size=dp(20), bold=True,
                               color=get_color_from_hex(COLORS['secondary'])))
        layout.add_widget(header)
        
        # Stats
        bankroll = data_manager.bankroll
        stats = GridLayout(cols=2, spacing=dp(10), size_hint_y=0.25)
        profit = bankroll['current_balance'] - bankroll['initial_balance']
        stats.add_widget(MetricCard('💵 Solde', f"{bankroll['current_balance']:.2f}€",
                                   f"+{profit:.2f}€" if profit >= 0 else f"{profit:.2f}€"))
        stats.add_widget(MetricCard('📊 ROI', f"{bankroll['roi']:.1f}%"))
        stats.add_widget(MetricCard('🎯 Win Rate', f"{bankroll['win_rate']:.1f}%"))
        stats.add_widget(MetricCard('🎰 Paris', str(bankroll['total_bets'])))
        layout.add_widget(stats)
        
        # Actions
        actions = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=0.2)
        
        deposit_row = BoxLayout(spacing=dp(10))
        self.deposit_input = TextInput(hint_text='Montant', input_filter='float',
                                       multiline=False, font_size=dp(16), size_hint_x=0.6)
        deposit_btn = Button(text='➕ Déposer', font_size=dp(16), size_hint_x=0.4,
                            background_normal='', background_color=get_color_from_hex(COLORS['success']))
        deposit_btn.bind(on_press=self.deposit)
        deposit_row.add_widget(self.deposit_input)
        deposit_row.add_widget(deposit_btn)
        actions.add_widget(deposit_row)
        
        withdraw_row = BoxLayout(spacing=dp(10))
        self.withdraw_input = TextInput(hint_text='Montant', input_filter='float',
                                        multiline=False, font_size=dp(16), size_hint_x=0.6)
        withdraw_btn = Button(text='➖ Retirer', font_size=dp(16), size_hint_x=0.4,
                             background_normal='', background_color=get_color_from_hex(COLORS['danger']))
        withdraw_btn.bind(on_press=self.withdraw)
        withdraw_row.add_widget(self.withdraw_input)
        withdraw_row.add_widget(withdraw_btn)
        actions.add_widget(withdraw_row)
        layout.add_widget(actions)
        
        # Historique
        layout.add_widget(Label(text='─── Transactions ───', font_size=dp(14),
                               color=get_color_from_hex(COLORS['gray']), size_hint_y=0.05))
        
        scroll = ScrollView(size_hint_y=0.4)
        history = BoxLayout(orientation='vertical', spacing=dp(5), size_hint_y=None)
        history.bind(minimum_height=history.setter('height'))
        
        icons = {'deposit': '➕', 'withdrawal': '➖', 'win': '🏆', 'loss': '❌'}
        colors = {'deposit': COLORS['success'], 'withdrawal': COLORS['accent'],
                 'win': COLORS['success'], 'loss': COLORS['danger']}
        
        for tx in bankroll['transactions'][-10:][::-1]:
            t, amt = tx.get('type', ''), tx.get('amount', 0)
            history.add_widget(Label(
                text=f"{icons.get(t, '•')} {t.upper()}: {amt:+.2f}€",
                font_size=dp(12), color=get_color_from_hex(colors.get(t, COLORS['text'])),
                size_hint_y=None, height=dp(25)
            ))
        
        scroll.add_widget(history)
        layout.add_widget(scroll)
        self.add_widget(layout)
    
    def deposit(self, instance):
        try:
            amt = float(self.deposit_input.text)
            if amt <= 0: return
            data_manager.bankroll['current_balance'] += amt
            if data_manager.bankroll['initial_balance'] == 0:
                data_manager.bankroll['initial_balance'] = amt
            data_manager.bankroll['transactions'].append({
                'type': 'deposit', 'amount': amt, 'timestamp': datetime.now().isoformat()
            })
            data_manager.save_bankroll()
            self.manager.current = 'home'
            self.manager.current = 'bankroll'
        except: pass
    
    def withdraw(self, instance):
        try:
            amt = float(self.withdraw_input.text)
            if amt <= 0 or amt > data_manager.bankroll['current_balance']: return
            data_manager.bankroll['current_balance'] -= amt
            data_manager.bankroll['transactions'].append({
                'type': 'withdrawal', 'amount': -amt, 'timestamp': datetime.now().isoformat()
            })
            data_manager.save_bankroll()
            self.manager.current = 'home'
            self.manager.current = 'bankroll'
        except: pass

# =============================================================================
# ÉCRAN APPRENTISSAGE
# =============================================================================
class LearningScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        with self.layout.canvas.before:
            Color(*get_color_from_hex(COLORS['dark']))
            self.bg = RoundedRectangle(pos=self.layout.pos, size=self.layout.size)
        
        # Header
        header = BoxLayout(size_hint_y=0.1)
        back = Button(text='← Retour', font_size=dp(16), size_hint_x=0.3,
                     background_normal='', background_color=get_color_from_hex(COLORS['darker']))
        back.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        header.add_widget(back)
        header.add_widget(Label(text='🧠 Apprentissage', font_size=dp(20), bold=True,
                               color=get_color_from_hex(COLORS['primary'])))
        self.layout.add_widget(header)
        
        self.content = BoxLayout(orientation='vertical', spacing=dp(10), size_hint_y=0.9)
        self.layout.add_widget(self.content)
        self.add_widget(self.layout)
    
    def on_enter(self):
        self.content.clear_widgets()
        scanner = self.manager.get_screen('scanner')
        
        if not scanner.current_prediction:
            self.content.add_widget(Label(
                text='👆 Lancez d\'abord une analyse dans Scanner',
                font_size=dp(16), color=get_color_from_hex(COLORS['gray'])
            ))
            return
        
        pred = scanner.current_prediction
        
        # Match info
        self.content.add_widget(Label(
            text=f"⚽ {pred['home']} vs {pred['away']}",
            font_size=dp(22), bold=True, color=get_color_from_hex(COLORS['text']),
            size_hint_y=0.2
        ))
        self.content.add_widget(Label(
            text=f"Cote: {pred['odds']:.2f} • Prob: {pred['probability']*100:.1f}%",
            font_size=dp(14), color=get_color_from_hex(COLORS['gray']), size_hint_y=0.1
        ))
        self.content.add_widget(Label(
            text=f"Mise suggérée: {pred['stake']:.2f}€",
            font_size=dp(16), color=get_color_from_hex(COLORS['accent']), size_hint_y=0.1
        ))
        
        # Question
        self.content.add_widget(Label(
            text='Le pronostic était-il correct?',
            font_size=dp(18), color=get_color_from_hex(COLORS['text']), size_hint_y=0.1
        ))
        
        # Boutons
        buttons = BoxLayout(spacing=dp(20), size_hint_y=0.2)
        win = Button(text='✅ GAGNÉ', font_size=dp(20), bold=True,
                    background_normal='', background_color=get_color_from_hex(COLORS['success']))
        win.bind(on_press=lambda x: self._train(True))
        buttons.add_widget(win)
        
        loss = Button(text='❌ PERDU', font_size=dp(20), bold=True,
                     background_normal='', background_color=get_color_from_hex(COLORS['danger']))
        loss.bind(on_press=lambda x: self._train(False))
        buttons.add_widget(loss)
        self.content.add_widget(buttons)
        
        # Stats
        brain = data_manager.brain
        self.content.add_widget(Label(
            text=f"📊 Cycles: {brain['total_cycles']} • Précision: {brain['accuracy']*100:.1f}%",
            font_size=dp(14), color=get_color_from_hex(COLORS['gray']), size_hint_y=0.1
        ))
    
    def _train(self, success):
        scanner = self.manager.get_screen('scanner')
        pred = scanner.current_prediction
        if not pred: return
        
        brain, bankroll = data_manager.brain, data_manager.bankroll
        
        # Mise à jour IA
        new_w, new_v = LearningEngine.update_weights(brain, success, pred['factors'].keys())
        brain['weights'], brain['velocity'] = new_w, new_v
        brain['total_cycles'] += 1
        brain['history'].append({'match': f"{pred['home']} vs {pred['away']}",
                                'result': 'win' if success else 'loss', 'timestamp': pred['timestamp']})
        wins = sum(1 for h in brain['history'] if h['result'] == 'win')
        brain['accuracy'] = wins / len(brain['history'])
        
        # Bankroll
        if pred['stake'] > 0:
            bankroll['total_bets'] += 1
            bankroll['total_wagered'] += pred['stake']
            if success:
                gain = pred['stake'] * pred['odds']
                bankroll['current_balance'] += gain - pred['stake']
                bankroll['total_won'] += gain - pred['stake']
                bankroll['transactions'].append({'type': 'win', 'amount': gain})
            else:
                bankroll['total_lost'] += pred['stake']
                bankroll['transactions'].append({'type': 'loss', 'amount': -pred['stake']})
            
            if bankroll['total_wagered'] > 0:
                bankroll['roi'] = (bankroll['total_won'] - bankroll['total_lost']) / bankroll['total_wagered'] * 100
            w_tx = sum(1 for tx in bankroll['transactions'] if tx['type'] == 'win')
            total_tx = w_tx + sum(1 for tx in bankroll['transactions'] if tx['type'] == 'loss')
            if total_tx > 0: bankroll['win_rate'] = w_tx / total_tx * 100
        
        data_manager.save_brain()
        data_manager.save_bankroll()
        scanner.current_prediction = None
        
        Popup(title='🧠 IA Entraînée!', content=Label(
            text=f"Précision: {brain['accuracy']*100:.1f}%\nROI: {bankroll['roi']:.1f}%",
            font_size=dp(16)), size_hint=(0.8, 0.4)).open()
        
        Clock.schedule_once(lambda dt: setattr(self.manager, 'current', 'home'), 2)

# =============================================================================
# ÉCRAN STATS
# =============================================================================
class StatsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        with layout.canvas.before:
            Color(*get_color_from_hex(COLORS['dark']))
            self.bg = RoundedRectangle(pos=layout.pos, size=layout.size)
        
        # Header
        header = BoxLayout(size_hint_y=0.1)
        back = Button(text='← Retour', font_size=dp(16), size_hint_x=0.3,
                     background_normal='', background_color=get_color_from_hex(COLORS['darker']))
        back.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        header.add_widget(back)
        header.add_widget(Label(text='📊 Statistiques', font_size=dp(20), bold=True,
                               color=get_color_from_hex(COLORS['accent'])))
        layout.add_widget(header)
        
        # Poids IA
        layout.add_widget(Label(text='─── Poids de l\'IA ───', font_size=dp(16),
                               color=get_color_from_hex(COLORS['gray']), size_hint_y=0.05))
        
        brain = data_manager.brain
        weights_box = BoxLayout(orientation='vertical', spacing=dp(8), size_hint_y=0.5)
        
        for factor, weight in sorted(brain['weights'].items(), key=lambda x: x[1], reverse=True):
            row = BoxLayout(spacing=dp(5))
            row.add_widget(Label(text=factor, font_size=dp(14),
                                color=get_color_from_hex(COLORS['text']), size_hint_x=0.3))
            row.add_widget(ProgressBar(value=weight*100, max=100, size_hint_x=0.5))
            row.add_widget(Label(text=f"{weight*100:.1f}%", font_size=dp(12),
                                color=get_color_from_hex(COLORS['accent']), size_hint_x=0.2))
            weights_box.add_widget(row)
        layout.add_widget(weights_box)
        
        # Stats globales
        layout.add_widget(Label(text='─── Performances ───', font_size=dp(16),
                               color=get_color_from_hex(COLORS['gray']), size_hint_y=0.05))
        
        bankroll = data_manager.bankroll
        global_stats = GridLayout(cols=2, spacing=dp(10), size_hint_y=0.2)
        global_stats.add_widget(MetricCard('🎯 Cycles', str(brain['total_cycles'])))
        global_stats.add_widget(MetricCard('📊 Précision', f"{brain['accuracy']*100:.1f}%"))
        global_stats.add_widget(MetricCard('💰 Misé', f"{bankroll['total_wagered']:.2f}€"))
        global_stats.add_widget(MetricCard('🏆 Gains', f"{bankroll['total_won']:.2f}€"))
        layout.add_widget(global_stats)
        
        # Reset
        reset = Button(text='🧨 Réinitialiser', font_size=dp(14), size_hint_y=0.1,
                      background_normal='', background_color=get_color_from_hex(COLORS['danger']))
        reset.bind(on_press=self._reset)
        layout.add_widget(reset)
        
        self.add_widget(layout)
    
    def _reset(self, instance):
        data_manager.brain = data_manager._load_brain()
        data_manager.bankroll = data_manager._load_bankroll()
        data_manager.save_brain()
        data_manager.save_bankroll()
        self.manager.current = 'home'
        self.manager.current = 'stats'

# =============================================================================
# ÉCRAN PARAMÈTRES
# =============================================================================
class SettingsScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(10))
        
        with layout.canvas.before:
            Color(*get_color_from_hex(COLORS['dark']))
            self.bg = RoundedRectangle(pos=layout.pos, size=layout.size)
        
        # Header
        header = BoxLayout(size_hint_y=0.1)
        back = Button(text='← Retour', font_size=dp(16), size_hint_x=0.3,
                     background_normal='', background_color=get_color_from_hex(COLORS['darker']))
        back.bind(on_press=lambda x: setattr(self.manager, 'current', 'home'))
        header.add_widget(back)
        header.add_widget(Label(text='⚙️ Paramètres', font_size=dp(20), bold=True,
                               color=get_color_from_hex(COLORS['gray'])))
        layout.add_widget(header)
        
        # Settings
        settings_box = BoxLayout(orientation='vertical', spacing=dp(15), size_hint_y=0.8)
        
        # API Key
        settings_box.add_widget(Label(text='🔑 Clé API Football', font_size=dp(14),
                                     color=get_color_from_hex(COLORS['text']), size_hint_y=0.08, halign='left'))
        self.api_input = TextInput(text=data_manager.settings.get('api_key', ''),
                                  hint_text='Clé RapidAPI', multiline=False, password=True,
                                  font_size=dp(14), size_hint_y=0.1)
        settings_box.add_widget(self.api_input)
        
        # Learning Rate
        self.lr_label = Label(
            text=f"📊 Learning Rate: {data_manager.settings.get('learning_rate', 0.05):.2f}",
            font_size=dp(14), color=get_color_from_hex(COLORS['text']), size_hint_y=0.08
        )
        settings_box.add_widget(self.lr_label)
        
        lr_slider = Slider(min=0.01, max=0.20,
                          value=data_manager.settings.get('learning_rate', 0.05), size_hint_y=0.1)
        lr_slider.bind(value=lambda i, v: setattr(self.lr_label, 'text', f"📊 Learning Rate: {v:.2f}"))
        settings_box.add_widget(lr_slider)
        
        # Kelly Fraction
        self.kelly_label = Label(
            text=f"💰 Kelly Fraction: {data_manager.settings.get('kelly_fraction', 0.25)*100:.0f}%",
            font_size=dp(14), color=get_color_from_hex(COLORS['text']), size_hint_y=0.08
        )
        settings_box.add_widget(self.kelly_label)
        
        kelly_slider = Slider(min=0.1, max=1.0,
                             value=data_manager.settings.get('kelly_fraction', 0.25), size_hint_y=0.1)
        kelly_slider.bind(value=lambda i, v: setattr(self.kelly_label, 'text', f"💰 Kelly Fraction: {v*100:.0f}%"))
        settings_box.add_widget(kelly_slider)
        
        # Save button
        def save(instance):
            data_manager.settings['api_key'] = self.api_input.text
            data_manager.settings['learning_rate'] = lr_slider.value
            data_manager.settings['kelly_fraction'] = kelly_slider.value
            data_manager.save_settings()
            Popup(title='✅ Sauvegardé', content=Label(text='Paramètres enregistrés'),
                 size_hint=(0.6, 0.2)).open()
        
        save_btn = Button(text='💾 Sauvegarder', font_size=dp(16), size_hint_y=0.12,
                         background_normal='', background_color=get_color_from_hex(COLORS['primary']))
        save_btn.bind(on_press=save)
        settings_box.add_widget(save_btn)
        
        # Info
        settings_box.add_widget(Label(text='Elite Neural Evolve v8.0.0\nPar Elite AI Team',
                                     font_size=dp(12), color=get_color_from_hex(COLORS['gray']), size_hint_y=0.1))
        
        layout.add_widget(settings_box)
        self.add_widget(layout)

# =============================================================================
# APPLICATION PRINCIPALE
# =============================================================================
class EliteNeuralApp(App):
    def build(self):
        Window.clearcolor = get_color_from_hex(COLORS['dark'])
        sm = ScreenManager(transition=FadeTransition(duration=0.2))
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(ScannerScreen(name='scanner'))
        sm.add_widget(BankrollScreen(name='bankroll'))
        sm.add_widget(LearningScreen(name='learning'))
        sm.add_widget(StatsScreen(name='stats'))
        sm.add_widget(SettingsScreen(name='settings'))
        return sm
    
    def on_start(self):
        try:
            from android.permissions import request_permission, Permission
            request_permission(Permission.WRITE_EXTERNAL_STORAGE)
            request_permission(Permission.READ_EXTERNAL_STORAGE)
        except: pass
    
    def on_stop(self):
        data_manager.save_brain()
        data_manager.save_bankroll()
        data_manager.save_settings()

if __name__ == '__main__':
    EliteNeuralApp().run()
    [app]

# Titre de l'application
title = Elite Neural Evolve

# Nom du package
package.name = eliteneural

# Domaine du package
package.domain = ai.elite

# Dossier source
source.dir = .

# Extensions à inclure
source.include_exts = py,png,jpg,kv,json,txt

# Version
version = 8.0.0

# Requirements (dépendances)
requirements = python3,kivy,numpy

# Icône
icon.filename = assets/icon.png

# Splash screen
presplash.filename = assets/splash.png

# Orientation
orientation = portrait

# Plein écran
fullscreen = 0

# Permissions Android
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET,VIBRATE

# API Android cible
android.api = 33

# API minimum
android.minapi = 21

# NDK
android.ndk = 25b

# Accepter la licence SDK
android.accept_sdk_license = True

# Architectures
android.archs = arm64-v8a, armeabi-v7a

# Backup Android
android.allow_backup = True

# SDK Target
android.sdk_target = 33

# Branch p4a
p4a.branch = master

# Dépendances Gradle
android.gradle_dependencies = androidx.appcompat:appcompat:1.6.1

# Copier les libs
android.copy_libs = 1

[buildozer]

# Niveau de log
log_level = 2

# Dossier de build
build_dir = ./.buildozer

# Dossier de sortie
bin_dir = ./bin
