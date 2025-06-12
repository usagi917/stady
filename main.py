import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import date, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# --- 1. アプリの基本設定 ---
st.set_page_config(
    page_title="株価データ表示アプリ",
    page_icon="📈",
    layout="wide"
)

st.title('📈 株価データ表示アプリ')
st.markdown("---")

# --- 2. キャッシュ機能付きのデータ取得関数 ---
@st.cache_data(ttl=300)  # 5分間キャッシュ
def get_stock_data(ticker, start_date, end_date):
    """株価データを取得する関数（キャッシュ付き）"""
    try:
        # yfinanceでデータを取得
        stock = yf.Ticker(ticker)
        data = stock.history(start=start_date, end=end_date)
        
        if data.empty:
            return None, "データが見つかりませんでした。銘柄コードや期間を確認してください。"
        
        # 会社情報も取得
        info = stock.info
        company_name = info.get('longName', info.get('shortName', ticker))
        
        return data, company_name
    except Exception as e:
        return None, f"データ取得エラー: {str(e)}"

# --- 3. サイドバーでユーザー入力を受け取る ---
st.sidebar.header('⚙️ 設定')

# 銘柄コードの入力ボックス
default_ticker = '7203.T'  # デフォルトはトヨタ
ticker_symbol = st.sidebar.text_input(
    '銘柄コード', 
    default_ticker,
    help="日本株は証券コード + .T、米国株はティッカーシンボルを入力"
).upper().strip()

# よく使われる銘柄の例
st.sidebar.markdown("""
**📝 入力例:**
- 🇯🇵 日本株: `7203.T` (トヨタ), `6758.T` (ソニー)
- 🇺🇸 米国株: `AAPL` (Apple), `GOOGL` (Google)
- 🇺🇸 米国株: `TSLA` (Tesla), `MSFT` (Microsoft)
""")

# 期間の選択
today = date.today()
default_start_date = today - timedelta(days=365)

col1, col2 = st.sidebar.columns(2)
with col1:
    start_date = st.date_input('📅 開始日', default_start_date)
with col2:
    end_date = st.date_input('📅 終了日', today)

# 日付の妥当性チェック
if start_date >= end_date:
    st.sidebar.error("⚠️ 開始日は終了日より前にしてください")
    st.stop()

if end_date > today:
    st.sidebar.warning("⚠️ 終了日が未来の日付になっています")

# --- 4. メイン画面の処理 ---
if ticker_symbol:
    # データ取得
    with st.spinner('📊 データを取得中...'):
        data, result = get_stock_data(ticker_symbol, start_date, end_date)
    
    if data is None:
        st.error(f"❌ {result}")
        st.info("💡 銘柄コードの形式を確認してください。日本株の場合は証券コード + `.T` が必要です。")
    else:
        # 会社名の表示
        company_name = result if isinstance(result, str) else ticker_symbol
        st.header(f'📊 {company_name} ({ticker_symbol})')
        
        # 基本統計情報
        col1, col2, col3, col4 = st.columns(4)
        
        latest_price = data['Close'].iloc[-1]
        price_change = data['Close'].iloc[-1] - data['Close'].iloc[-2] if len(data) > 1 else 0
        price_change_pct = (price_change / data['Close'].iloc[-2] * 100) if len(data) > 1 else 0
        
        with col1:
            st.metric("💰 最新価格", f"{latest_price:.2f}", f"{price_change:+.2f}")
        with col2:
            st.metric("📈 変動率", f"{price_change_pct:+.2f}%")
        with col3:
            st.metric("📊 最高値", f"{data['High'].max():.2f}")
        with col4:
            st.metric("📉 最安値", f"{data['Low'].min():.2f}")
        
        st.markdown("---")
        
        # グラフ表示（Plotlyを使用してより美しく）
        st.subheader('📈 株価チャート')
        
        # ローソク足チャートと出来高チャート
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=('株価', '出来高'),
            row_width=[0.7, 0.3]
        )
        
        # ローソク足チャート
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name="株価"
            ),
            row=1, col=1
        )
        
        # 出来高チャート
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['Volume'],
                name="出来高",
                marker_color='lightblue'
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title=f"{company_name} 株価チャート",
            xaxis_rangeslider_visible=False,
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 簡単な移動平均線も表示
        st.subheader('📊 移動平均線')
        
        # 移動平均を計算
        data['MA5'] = data['Close'].rolling(window=5).mean()
        data['MA25'] = data['Close'].rolling(window=25).mean()
        
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(x=data.index, y=data['Close'], name='終値', line=dict(color='blue')))
        fig2.add_trace(go.Scatter(x=data.index, y=data['MA5'], name='5日移動平均', line=dict(color='orange')))
        fig2.add_trace(go.Scatter(x=data.index, y=data['MA25'], name='25日移動平均', line=dict(color='red')))
        
        fig2.update_layout(
            title="終値と移動平均線",
            xaxis_title="日付",
            yaxis_title="価格",
            height=400
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        
        # データテーブル表示
        st.subheader('📋 株価データ詳細')
        
        # 表示用データの準備
        display_data = data.copy()
        display_data = display_data.drop(columns=['Adj Close'] if 'Adj Close' in display_data.columns else [])
        display_data.rename(columns={
            'Open': '始値', 'High': '高値', 'Low': '安値', 
            'Close': '終値', 'Volume': '出来高',
            'MA5': '5日移動平均', 'MA25': '25日移動平均'
        }, inplace=True)
        
        # 数値の丸め
        numeric_columns = ['始値', '高値', '安値', '終値', '5日移動平均', '25日移動平均']
        for col in numeric_columns:
            if col in display_data.columns:
                display_data[col] = display_data[col].round(2)
        
        # 最新の日付が上に来るように並び替え
        display_data_sorted = display_data.sort_index(ascending=False)
        st.dataframe(display_data_sorted, use_container_width=True)
        
        # CSVダウンロードボタン
        st.subheader('💾 データダウンロード')
        
        csv = display_data_sorted.to_csv(index=True).encode('utf-8-sig')
        st.download_button(
            label="📥 CSVファイルをダウンロード",
            data=csv,
            file_name=f'{ticker_symbol}_{start_date}_to_{end_date}.csv',
            mime='text/csv',
        )
        
        # 追加情報
        st.markdown("---")
        st.info(f"📊 データ期間: {start_date} ～ {end_date} ({len(data)}日分のデータ)")

else:
    st.info('👈 サイドバーで銘柄コードを入力してください。')
    
    # サンプル画像やヘルプを表示
    st.markdown("""
    ## 🚀 使い方
    
    1. **サイドバー**で銘柄コードを入力
    2. **期間**を選択
    3. **株価チャート**と**データ**を確認
    4. 必要に応じて**CSVダウンロード**
    
    ## 💡 対応銘柄
    
    - **🇯🇵 日本株**: 証券コード + `.T` (例: `7203.T`)
    - **🇺🇸 米国株**: ティッカーシンボル (例: `AAPL`)
    
    ## ⚡ 機能
    
    - リアルタイム株価データ
    - ローソク足チャート
    - 移動平均線表示
    - 出来高チャート
    - CSVエクスポート
    """)