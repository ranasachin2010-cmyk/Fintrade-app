# V16.4 NO ELIF - WHATSAPP PROOF
def get_signal(df):
    # ... simple if only ...
    final = 'HOLD'
    color = '#FFD700'
    if score >= 2:
        final = 'BUY'
        color = '#00FF00'
    if score <= -2:
        final = 'SELL'
        color = '#FF0000'
    return final, color, last_rsi, reasons, score
