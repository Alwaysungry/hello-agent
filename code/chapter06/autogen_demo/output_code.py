import streamlit as st
import requests
import time
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import json
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List
import functools
from dataclasses import dataclass
import logging
from logging.handlers import RotatingFileHandler
import random
from functools import wraps

# ==================== 日志配置 ====================
class AppLogger:
    """应用日志记录器"""
    
    def __init__(self, name: str = "bitcoin_tracker"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        if not self.logger.handlers:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            file_handler = RotatingFileHandler(
                'app.log',
                maxBytes=1024*1024,
                backupCount=5
            )
            file_handler.setLevel(logging.DEBUG)
            
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)
            
            self.logger.addHandler(console_handler)
            self.logger.addHandler(file_handler)
    
    def log_api_call(self, url: str, status: str, duration: float):
        self.logger.info(f"API调用: {url} - 状态: {status} - 耗时: {duration:.2f}s")
    
    def log_error(self, error_type: str, message: str, exc_info=None):
        self.logger.error(f"{error_type}: {message}", exc_info=exc_info)
    
    def log_user_action(self, action: str, details: dict = None):
        details_str = f" - 详情: {details}" if details else ""
        self.logger.info(f"用户操作: {action}{details_str}")

# ==================== 配置管理 ====================
class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.default_config = {
            "api": {
                "base_url": "https://api.coingecko.com/api/v3",
                "timeout": 10,
                "rate_limit": 30,
                "max_retries": 3,
                "cache_ttl": 30
            },
            "app": {
                "refresh_interval": 30,
                "theme": "dark",
                "chart_days": 1,
                "max_cache_items": 100
            },
            "ui": {
                "chart_height": 400,
                "show_market_info": True,
                "show_statistics": True,
                "enable_auto_refresh": False
            }
        }
        self.config = self.load_config()
    
    def load_config(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    return self._deep_merge(self.default_config, user_config)
            except (json.JSONDecodeError, IOError) as e:
                print(f"加载配置文件失败: {e}, 使用默认配置")
                return self.default_config
        return self.default_config
    
    def _deep_merge(self, base: dict, update: dict) -> dict:
        result = base.copy()
        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def save_config(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def get(self, key: str, default=None):
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value):
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save_config()

# ==================== 主题管理 ====================
class ThemeManager:
    """主题管理器"""
    
    THEMES = {
        'dark': {
            'background': 'rgba(0,0,0,0)',
            'text_color': 'white',
            'grid_color': 'rgba(128, 128, 128, 0.2)',
            'up_color': '#00FF00',
            'down_color': '#FF4444',
            'card_bg': 'rgba(30, 30, 30, 0.7)',
            'primary_color': '#F7931A'
        },
        'light': {
            'background': 'white',
            'text_color': 'black',
            'grid_color': 'rgba(128, 128, 128, 0.1)',
            'up_color': '#00AA00',
            'down_color': '#AA0000',
            'card_bg': 'rgba(240, 240, 240, 0.9)',
            'primary_color': '#E67E22'
        }
    }
    
    @classmethod
    def get_colors(cls, theme: str = 'dark'):
        return cls.THEMES.get(theme, cls.THEMES['dark'])

# ==================== 性能监控装饰器 ====================
def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            if 'performance_stats' not in st.session_state:
                st.session_state.performance_stats = {}
            
            func_name = func.__name__
            if func_name not in st.session_state.performance_stats:
                st.session_state.performance_stats[func_name] = {
                    'count': 0,
                    'total_time': 0,
                    'avg_time': 0,
                    'min_time': float('inf'),
                    'max_time': 0
                }
            
            stats = st.session_state.performance_stats[func_name]
            stats['count'] += 1
            stats['total_time'] += duration
            stats['avg_time'] = stats['total_time'] / stats['count']
            stats['min_time'] = min(stats['min_time'], duration)
            stats['max_time'] = max(stats['max_time'], duration)
            
            if duration > 5.0:
                st.warning(f"函数 {func_name} 执行时间过长: {duration:.2f}秒")
            
            return result
        except Exception as e:
            duration = time.time() - start_time
            st.error(f"函数 {func.__name__} 执行失败，耗时 {duration:.2f}秒: {str(e)}")
            raise
    
    return wrapper

# ==================== 缓存管理 ====================
CACHE_NAMESPACE = "__cache__"

def cleanup_cache():
    current_time = time.time()
    keys_to_delete = []
    
    for key in list(st.session_state.keys()):
        if key.startswith(CACHE_NAMESPACE):
            if isinstance(st.session_state[key], tuple) and len(st.session_state[key]) == 2:
                _, timestamp = st.session_state[key]
                if current_time - timestamp > 300:
                    keys_to_delete.append(key)
    
    for key in keys_to_delete:
        del st.session_state[key]

def cache_with_expiry(seconds: int = 30):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{CACHE_NAMESPACE}_{func.__name__}_{hash(str(args) + str(kwargs))}"
            
            if cache_key in st.session_state:
                cached_data, timestamp = st.session_state[cache_key]
                if time.time() - timestamp < seconds:
                    return cached_data
            
            result = func(*args, **kwargs)
            
            if result is not None:
                st.session_state[cache_key] = (result, time.time())
            
            if random.random() < 0.1:
                cleanup_cache()
            
            return result
        return wrapper
    return decorator

# ==================== 数据模型 ====================
@dataclass
class BitcoinPriceData:
    """比特币价格数据模型"""
    current_price: float
    price_change_24h: float
    price_change_amount_24h: float
    market_cap: float
    volume_24h: float
    last_updated: int
    price_history: List[List[float]]
    timestamp: float
    
    @property
    def is_positive(self) -> bool:
        return self.price_change_24h > 0 if self.price_change_24h is not None else False

# ==================== 格式化工具 ====================
class DataFormatter:
    """数据格式化工具类"""
    
    @staticmethod
    def format_currency(value: Optional[float], currency: str = 'USD') -> str:
        if value is None:
            return "N/A"
        return f"{currency} {value:,.2f}"
    
    @staticmethod
    def format_percentage(value: Optional[float], decimals: int = 2) -> str:
        if value is None:
            return "N/A"
        sign = '+' if value > 0 else ''
        return f"{sign}{value:.{decimals}f}%"
    
    @staticmethod
    def format_timestamp(timestamp: Optional[int], 
                         format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
        if not timestamp:
            return "N/A"
        try:
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime(format_str)
        except (ValueError, TypeError):
            return "N/A"
    
    @staticmethod
    def format_large_number(value: Optional[float]) -> str:
        if value is None:
            return "N/A"
        
        if value >= 1_000_000_000:
            return f"${value/1_000_000_000:.2f}B"
        elif value >= 1_000_000:
            return f"${value/1_000_000:.2f}M"
        else:
            return f"${value:,.0f}"

# ==================== 比特币价格服务 ====================
class BitcoinPriceService:
    """比特币价格服务类"""
    
    def __init__(self, config: ConfigManager, logger: AppLogger):
        self.config = config
        self.logger = logger
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BitcoinPriceTracker/2.0',
            'Accept': 'application/json'
        })
    
    @monitor_performance
    def validate_price_data(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        if not data:
            return False, "数据为空"
        
        required_fields = {
            'current_price': (float, "当前价格"),
            'price_change_24h': (float, "24小时涨跌幅"),
            'last_updated': (int, "最后更新时间")
        }
        
        for field, (field_type, field_name) in required_fields.items():
            if field not in data:
                return False, f"缺少必需字段: {field_name}"
            
            if data[field] is None:
                return False, f"{field_name}为空"
            
            if not isinstance(data[field], field_type):
                return False, f"{field_name}类型错误"
        
        if data['current_price'] <= 0:
            return False, "价格必须大于0"
        
        if data['current_price'] > 1000000:
            return False, "价格异常偏高"
        
        try:
            update_time = datetime.fromtimestamp(data['last_updated'])
            current_time = datetime.now()
            
            if update_time > current_time + timedelta(hours=1):
                return False, "更新时间在未来"
            if update_time < current_time - timedelta(days=7):
                return False, "数据过于陈旧"
        except (ValueError, TypeError):
            return False, "时间戳格式错误"
        
        return True, "验证通过"
    
    @monitor_performance
    @cache_with_expiry(seconds=30)
    def fetch_bitcoin_data(self) -> Optional[BitcoinPriceData]:
        max_retries = self.config.get('api.max_retries', 3)
        timeout = self.config.get('api.timeout', 10)
        base_url = self.config.get('api.base_url')
        
        for attempt in range(max_retries):
            start_time = time.time()
            try:
                price_url = f"{base_url}/simple/price"
                price_params = {
                    'ids': 'bitcoin',
                    'vs_currencies': 'usd',
                    'include_24hr_change': 'true',
                    'include_24hr_vol': 'true',
                    'include_market_cap': 'true',
                    'include_last_updated_at': 'true'
                }
                
                price_response = self.session.get(
                    price_url, 
                    params=price_params, 
                    timeout=timeout
                )
                price_response.raise_for_status()
                price_data = price_response.json()
                
                chart_url = f"{base_url}/coins/bitcoin/market_chart"
                chart_params = {
                    'vs_currency': 'usd',
                    'days': str(self.config.get('app.chart_days', 1)),
                    'interval': 'hourly'
                }
                
                chart_response = self.session.get(
                    chart_url,
                    params=chart_params,
                    timeout=timeout
                )
                chart_response.raise_for_status()
                chart_data = chart_response.json()
                
                bitcoin_data = price_data.get('bitcoin', {})
                
                current_price = bitcoin_data.get('usd')
                price_change_pct = bitcoin_data.get('usd_24h_change')
                price_change_amount = 0
                if current_price and price_change_pct:
                    price_change_amount = current_price * (price_change_pct / 100)
                
                result_data = {
                    'current_price': current_price,
                    'price_change_24h': price_change_pct,
                    'price_change_amount_24h': price_change_amount,
                    'market_cap': bitcoin_data.get('usd_market_cap'),
                    'volume_24h': bitcoin_data.get('usd_24h_vol'),
                    'last_updated': bitcoin_data.get('last_updated_at'),
                    'price_history': chart_data.get('prices', []),
                    'timestamp': time.time()
                }
                
                is_valid, message = self.validate_price_data(result_data)
                
                if is_valid:
                    duration = time.time() - start_time
                    self.logger.log_api_call(price_url, "成功", duration)
                    return BitcoinPriceData(**result_data)
                else:
                    self.logger.log_error("数据验证失败", message)
                    
                    if attempt < max_retries - 1:
                        wait_time = 1 * (attempt + 1)
                        time.sleep(wait_time)
                        continue
                    else:
                        return None
                    
            except requests.exceptions.Timeout:
                duration = time.time() - start_time
                self.logger.log_error("请求超时", f"第{attempt + 1}次尝试超时，耗时: {duration:.2f}s")
                
                if attempt < max_retries - 1:
                    wait_time = 2 * (attempt + 1)
                    time.sleep(wait_time)
                    continue
                else:
                    st.error("请求超时，请检查网络连接")
                    return None
                    
            except requests.exceptions.RequestException as e:
                duration = time.time() - start_time
                self.logger.log_error("网络请求错误", str(e))
                
                if attempt == max_retries - 1:
                    st.error(f"网络请求失败: {str(e)}")
                    return None
                    
                wait_time = 1 * (attempt + 1)
                time.sleep(wait_time)
                
            except ValueError as e:
                self.logger.log_error("数据解析错误", str(e))
                st.error(f"数据解析错误: {str(e)}")
                return None
                
            except Exception as e:
                self.logger.log_error("未知错误", str(e), exc_info=True)
                st.error(f"未知错误: {str(e)}")
                return None
        
        return None

# ==================== 图表生成器 ====================
class ChartGenerator:
    """图表生成器类"""
    
    def __init__(self, config: ConfigManager, theme_manager: ThemeManager):
        self.config = config
        self.theme_manager = theme_manager
    
    @monitor_performance
    def create_price_chart(self, price_history: List[List[float]], 
                          title: str = "价格走势") -> Optional[go.Figure]:
        if not price_history or len(price_history) < 2:
            return None
        
        try:
            theme = self.config.get('app.theme', 'dark')
            colors = self.theme_manager.get_colors(theme)
            
            timestamps = [item[0] for item in price_history]
            prices = [item[1] for item in price_history]
            
            dates = [datetime.fromtimestamp(ts/1000) for ts in timestamps]
            
            first_price = prices[0]
            last_price = prices[-1]
            trend_color = colors['up_color'] if last_price >= first_price else colors['down_color']
            
            fig = go.Figure()
            
            fig.add_trace(go.Scatter(
                x=dates,
                y=prices,
                mode='lines',
                name='比特币价格',
                line=dict(color=trend_color, width=2),
                fill='tozeroy',
                fillcolor=f'rgba({int(trend_color[1:3], 16)}, {int(trend_color[3:5], 16)}, {int(trend_color[5:7],16)}, 0.1)',
                hovertemplate='<b>%{x|%H:%M}</b><br>$%{y:.2f}<extra></extra>'
            ))
            
            fig.add_trace(go.Scatter(
                x=[dates[-1]],
                y=[prices[-1]],
                mode='markers+text',
                name='当前价格',
                marker=dict(size=10, color='white', line=dict(width=2, color=trend_color)),
                text=[f'${prices[-1]:.2f}'],
                textposition='top center',
                showlegend=False
            ))
            
            fig.update_layout(
                title=dict(
                    text=title,
                    font=dict(size=16, color=colors['text_color'])
                ),
                xaxis=dict(
                    title="时间",
                    gridcolor=colors['grid_color'],
                    tickformat="%H:%M",
                    showgrid=True
                ),
                yaxis=dict(
                    title="价格 (USD)",
                    tickprefix="$",
                    gridcolor=colors['grid_color'],
                    showgrid=True
                ),
                template="plotly_dark" if theme == 'dark' else "plotly_white",
                hovermode="x unified",
                height=self.config.get('ui.chart_height', 400),
                margin=dict(l=20, r=20, t=50, b=20),
                plot_bgcolor=colors['background'],
                paper_bgcolor=colors['background']
            )
            
            return fig
            
        except Exception as e:
            st.error(f"生成图表时出错: {str(e)}")
            return None

# ==================== Streamlit应用 ====================
class BitcoinPriceApp:
    """比特币价格应用主类"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.logger = AppLogger()
        self.theme_manager = ThemeManager()
        self.formatter = DataFormatter()
        
        self.service = BitcoinPriceService(self.config, self.logger)
        self.chart_generator = ChartGenerator(self.config, self.theme_manager)
        
        self._init_session_state()
    
    def _init_session_state(self):
        defaults = {
            'price_data': None,
            'last_update': None,
            'auto_refresh': self.config.get('ui.enable_auto_refresh', False),
            'last_manual_refresh': 0,
            'theme': self.config.get('app.theme', 'dark'),
            'refresh_count': 0,
            'error_count': 0,
            'user_preferences': {}
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def setup_page(self):
        st.set_page_config(
            page_title="Bitcoin Price Tracker Pro",
            page_icon="₿",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        self._apply_custom_css()
    
    def _apply_custom_css(self):
        theme = st.session_state.theme
        colors = self.theme_manager.get_colors(theme)
        
        css = f"""
        <style>
        .main-header {{
            font-size: 2.5rem;
            font-weight: bold;
            color: {colors['primary_color']};
            text-align: center;
            margin-bottom: 1rem;
        }}
        .price-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 10px;
            padding: 20px;
            color: white;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        .metric-card {{
            background: {colors['card_bg']};
            border-radius: 10px;
            padding: 15px;
            border-left: 4px solid {colors['primary_color']};
        }}
        .positive {{
            color: {colors['up_color']};
        }}
        .negative {{
            color: {colors['down_color']};
        }}
        .stButton > button {{
            width: 100%;
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    
    def render_sidebar(self):
        with st.sidebar:
            st.title("⚙️ 设置")
            
            theme_options = ["dark", "light"]
            current_theme = st.session_state.theme
            theme_index = theme_options.index(current_theme) if current_theme in theme_options else 0
            
            new_theme = st.selectbox(
                "选择主题",
                theme_options,
                index=theme_index
            )
            
            if new_theme != st.session_state.theme:
                st.session_state.theme = new_theme
                self.config.set('app.theme', new_theme)
                self.logger.log_user_action("切换主题", {"theme": new_theme})
                st.rerun()
            
            col1, col2 = st.columns(2)
            with col1:
                auto_refresh = st.checkbox(
                    "自动刷新",
                    value=st.session_state.auto_refresh,
                    help="启用自动刷新功能"
                )
            
            with col2:
                if auto_refresh:
                    refresh_intervals = [30, 60, 120]
                    current_interval = self.config.get('app.refresh_interval', 30)
                    interval_index = refresh_intervals.index(current_interval) if current_interval in refresh_intervals else 0
                    
                    refresh_interval = st.selectbox(
                        "刷新间隔(秒)",
                        refresh_intervals,
                        index=interval_index,
                        help="自动刷新的时间间隔"
                    )
                    
                    if refresh_interval != current_interval:
                        self.config.set('app.refresh_interval', refresh_interval)
                else:
                    refresh_interval = self.config.get('app.refresh_interval', 30)
            
            if auto_refresh != st.session_state.auto_refresh:
                st.session_state.auto_refresh = auto_refresh
                self.config.set('ui.enable_auto_refresh', auto_refresh)
                self.logger.log_user_action("切换自动刷新", {"enabled": auto_refresh})
                st.rerun()
            
            st.markdown("---")
            
            st.subheader("📊 图表设置")
            chart_days = st.selectbox(
                "图表显示天数",
                [1, 7, 30],
                index=0,
                help="价格图表显示的天数范围"
            )
            
            if chart_days != self.config.get('app.chart_days', 1):
                self.config.set('app.chart_days', chart_days)
                st.session_state.price_data = None
                st.rerun()
            
            st.markdown("---")
            
            if self.config.get('ui.show_statistics', True):
                st.subheader("📈 统计")
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("刷新次数", st.session_state.refresh_count)
                with col2:
                    st.metric("错误次数", st.session_state.error_count)
            
            st.markdown("---")
            
            st.subheader("ℹ️ 关于")
            st.markdown("""
            **数据来源**: CoinGecko API  
            **更新频率**: 30秒/次  
            **版本**: 2.0.0  
            
            [API文档](https://www.coingecko.com/api/documentation)
            """)
            
            if st.checkbox("显示性能统计", False):
                st.markdown("---")
                st.subheader("⚡ 性能统计")
                if 'performance_stats' in st.session_state:
                    for func_name, stats in st.session_state.performance_stats.items():
                        st.text(f"{func_name}:")
                        st.text(f"  调用次数: {stats['count']}")
                        st.text(f"  平均耗时: {stats['avg_time']:.3f}s")
                        st.text(f"  最小耗时: {stats['min_time']:.3f}s")
                        st.text(f"  最大耗时: {stats['max_time']:.3f}s")
    
    def render_header(self):
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            st.markdown('<div class="main-header">₿ Bitcoin Price Tracker Pro</div>', 
                       unsafe_allow_html=True)
            st.markdown("实时比特币价格监控与数据分析")
        
        with col2:
            current_time = time.time()
            cooldown_remaining = max(0, 30 - (current_time - st.session_state.last_manual_refresh))
            
            if cooldown_remaining > 0:
                st.button(
                    f"🔄 冷却中 ({int(cooldown_remaining)}s)",
                    disabled=True,
                    use_container_width=True,
                    help="请等待冷却时间结束"
                )
            else:
                if st.button("🔄 刷新数据", use_container_width=True, help="手动刷新价格数据"):
                    st.session_state.last_manual_refresh = current_time
                    st.session_state.price_data = None
                    st.session_state.refresh_count += 1
                    self.logger.log_user_action("手动刷新")
                    st.rerun()
        
        with col3:
            if st.session_state.last_update:
                last_update_str = self.formatter.format_timestamp(
                    st.session_state.last_update,
                    "%H:%M:%S"
                )
                st.caption(f"最后更新: {last_update_str}")
            else:
                st.caption("等待数据...")
    
    def render_price_display(self, price_data: BitcoinPriceData):
        with st.container():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown('<div class="price-card">', unsafe_allow_html=True)
                st.markdown(f"### {self.formatter.format_currency(price_data.current_price)}")
                
                change_class = "positive" if price_data.is_positive else "negative"
                change_icon = "📈" if price_data.is_positive else "📉"
                
                col_change1, col_change2 = st.columns(2)
                with col_change1:
                    st.markdown(f'<div class="{change_class}">'
                               f'{change_icon} {self.formatter.format_percentage(price_data.price_change_24h)}'
                               '</div>', unsafe_allow_html=True)
                
                with col_change2:
                    change_amount = self.formatter.format_currency(
                        abs(price_data.price_change_amount_24h)
                    )
                    direction = "上涨" if price_data.is_positive else "下跌"
                    st.markdown(f'<div class="{change_class}">'
                               f'{direction} {change_amount}'
                               '</div>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                with st.container():
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric(
                        "市值",
                        self.formatter.format_large_number(price_data.market_cap)
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
            
            with col3:
                with st.container():
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.metric(
                        "24h交易量",
                        self.formatter.format_large_number(price_data.volume_24h)
                    )
                    st.markdown('</div>', unsafe_allow_html=True)
    
    def render_chart(self, price_data: BitcoinPriceData):
        if price_data.price_history:
            chart_title = f"{self.config.get('app.chart_days', 1)}天价格走势"
            fig = self.chart_generator.create_price_chart(price_data.price_history, chart_title)
            if fig:
                st.plotly_chart(fig, use_container_width=True, theme=st.session_state.theme)
    
    def render_market_info(self):
        if self.config.get('ui.show_market_info', True):
            st.markdown("---")
            st.subheader("📈 市场概览")
            
            cols = st.columns(4)
            market_info = [
                ("市值排名", "#1", "全球加密货币"),
                ("流通供应", "19.5M BTC", "约93%已流通"),
                ("总供应量", "21M BTC", "最大供应上限"),
                ("发行时间", "2009-01-03", "中本聪创世区块")
            ]
            
            for idx, (title, value, desc) in enumerate(market_info):
                with cols[idx]:
                    st.metric(title, value, desc)
    
    def handle_auto_refresh(self):
        if st.session_state.auto_refresh:
            current_time = time.time()
            last_update = st.session_state.last_update
            refresh_interval = self.config.get('app.refresh_interval', 30)
            
            if last_update and (current_time - last_update) > refresh_interval:
                with st.spinner(f"自动刷新中..."):
                    price_data = self.service.fetch_bitcoin_data()
                    if price_data:
                        st.session_state.price_data = price_data
                        st.session_state.last_update = current_time
                        st.session_state.refresh_count += 1
                        self.logger.log_user_action("自动刷新")
                        st.rerun()
            
            if last_update:
                next_refresh = last_update + refresh_interval
                time_left = max(0, next_refresh - current_time)
                
                progress = 1 - (time_left / refresh_interval)
                st.progress(progress, text=f"⏱️ 下次刷新: {int(time_left)}秒后")
    
    def render_footer(self):
        st.markdown("---")
        
        with st.expander("⚠️ 免责声明", expanded=False):
            st.markdown("""
            ### 重要声明
            
            1. **信息仅供参考**: 本应用提供的所有数据仅供参考，不构成任何投资建议。
            2. **数据准确性**: 数据来自第三方API，可能存在延迟或不准确的情况。
            3. **投资风险**: 加密货币价格波动剧烈，投资需谨慎，风险自负。
            4. **技术风险**: 网络故障、API限制等因素可能影响数据获取。
            
            **使用本应用即表示您同意以上条款。**
            """)
        
        current_year = datetime.now().year
        st.caption(f"© {current_year} Bitcoin Price Tracker Pro • 版本 2.0.0 • 最后更新: {datetime.now().strftime('%Y-%m-%d')}")
    
    def run(self):
        try:
            self.setup_page()
            
            self.render_sidebar()
            
            self.render_header()
            
            if st.session_state.price_data is None:
                with st.spinner("正在获取比特币价格数据..."):
                    price_data = self.service.fetch_bitcoin_data()
                    
                    if price_data:
                        st.session_state.price_data = price_data
                        st.session_state.last_update = time.time()
                        st.rerun()
                    else:
                        st.error("无法获取比特币价格数据，请稍后重试。")
                        st.session_state.error_count += 1
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("🔄 重试", use_container_width=True):
                                st.session_state.price_data = None
                                st.rerun()
                        with col2:
                            if st.button("📋 查看日志", use_container_width=True):
                                st.info("请查看应用目录下的 app.log 文件获取详细错误信息")
                        return
            
            self.render_price_display(st.session_state.price_data)
            
            self.render_chart(st.session_state.price_data)
            
            self.render_market_info()
            
            self.handle_auto_refresh()
            
            self.render_footer()
            
        except Exception as e:
            self.logger.log_error("应用运行错误", str(e), exc_info=True)
            st.error(f"应用运行出错: {str(e)}")
            st.info("请刷新页面重试，或检查日志文件获取详细信息。")

# ==================== 主程序入口 ====================
def main():
    try:
        app = BitcoinPriceApp()
        app.run()
    except Exception as e:
        logger = AppLogger()
        logger.log_error("应用启动失败", str(e), exc_info=True)
        
        st.error(f"应用启动失败: {str(e)}")
        st.info("""
        可能的原因：
        1. 网络连接问题
        2. 配置文件损坏
        3. 依赖包缺失
        
        请尝试：
        1. 检查网络连接
        2. 删除 config.json 文件后重试
        3. 重新安装依赖包
        """)

if __name__ == "__main__":
    main()