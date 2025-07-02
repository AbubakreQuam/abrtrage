from flask import Flask, render_template, request, send_file, redirect, url_for
from io import BytesIO
from reportlab.pdfgen import canvas
import os

app = Flask(__name__)

# Store latest result globally for PDF export
latest_result = {}

@app.route('/', methods=['GET', 'POST'])
def index():
    global latest_result
    result = None

    if request.method == 'POST':
        try:
            odds = request.form.getlist('odds')
            odds = [float(o) for o in odds if o and float(o) > 0]
            total_stake = float(request.form.get('total_stake'))

            inv_odds = [1 / o for o in odds]
            total_inverse = sum(inv_odds)

            if total_inverse < 1:
                stakes = [(inv / total_inverse) * total_stake for inv in inv_odds]
                returns = [stakes[i] * odds[i] for i in range(len(odds))]
                guaranteed_return = min(returns)
                profit = guaranteed_return - total_stake

                result = {
                    'arbitrage': True,
                    'odds': [round(o, 2) for o in odds],
                    'inv_odds': [round(inv, 4) for inv in inv_odds],
                    'total_inverse': round(total_inverse, 4),
                    'stakes': [round(s, 2) for s in stakes],
                    'returns': [round(r, 2) for r in returns],
                    'guaranteed_return': round(guaranteed_return, 2),
                    'profit': round(profit, 2),
                    'total_stake': round(total_stake, 2)
                }
                latest_result = result
            else:
                result = {
                    'arbitrage': False,
                    'total_inverse': round(total_inverse, 4),
                    'inv_odds': [round(inv, 4) for inv in inv_odds]
                }
                latest_result = result
        except Exception as e:
            result = {'error': str(e)}

    return render_template('index.html', result=result)

@app.route('/export')
def export():
    global latest_result
    buffer = BytesIO()
    p = canvas.Canvas(buffer)

    p.setFont("Helvetica", 14)
    p.drawString(100, 800, "Arbitrage Betting Report")
    p.setFont("Helvetica", 12)
    y = 770

    if latest_result.get('arbitrage'):
        for i, odd in enumerate(latest_result['odds']):
            p.drawString(100, y, f"Odd {i+1}: {odd}")
            y -= 20
        for i, inv in enumerate(latest_result['inv_odds']):
            p.drawString(100, y, f"1/Odd {i+1}: {inv}")
            y -= 20
        p.drawString(100, y, f"Sum of Inverses: {latest_result['total_inverse']}")
        y -= 20
        for i, stake in enumerate(latest_result['stakes']):
            p.drawString(100, y, f"Stake on Odd {i+1}: ₦{stake}")
            y -= 20
        for i, ret in enumerate(latest_result['returns']):
            p.drawString(100, y, f"Return if Odd {i+1} wins: ₦{ret}")
            y -= 20
        p.drawString(100, y, f"Guaranteed Return: ₦{latest_result['guaranteed_return']}")
        y -= 20
        p.drawString(100, y, f"Profit: ₦{latest_result['profit']}")
    else:
        p.drawString(100, y, "No Arbitrage Opportunity Found.")
        y -= 20
        p.drawString(100, y, f"Sum of Inverses: {latest_result.get('total_inverse', 'N/A')}")
        y -= 20
        if 'inv_odds' in latest_result:
            for i, inv in enumerate(latest_result['inv_odds']):
                p.drawString(100, y, f"1/Odd {i+1}: {inv}")
                y -= 20

    p.showPage()
    p.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name="arbitrage_report.pdf", mimetype='application/pdf')



if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
# This is the main Flask application for the Arbitrage Betting Calculator
# It handles the main logic for calculating arbitrage opportunities and exporting results as a PDF.
