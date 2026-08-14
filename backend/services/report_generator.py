"""PDF report generation for stocks, insights, and portfolio."""

from __future__ import annotations

from datetime import datetime


class ReportGenerator:
    """Generate professional PDF reports."""

    def __init__(self) -> None:
        """Initialize report generator."""
        self.width = 595  # A4 width in points
        self.height = 842  # A4 height in points

    def generate_stock_report(
        self,
        symbol: str,
        name: str,
        price: float,
        change_pct: float,
        sentiment: str,
        summary: str,
        recommendation: str,
        catalysts: list[str],
        risks: list[str],
    ) -> bytes:
        """Generate PDF stock research report.

        Returns:
            PDF as bytes
        """
        html_content = self._generate_stock_html(
            symbol, name, price, change_pct, sentiment, summary, recommendation, catalysts, risks
        )
        return self._html_to_pdf(html_content)

    def generate_portfolio_report(
        self,
        holdings: list[dict[str, object]],
        metrics: dict[str, object],
        generated_at: str | None = None,
    ) -> bytes:
        """Generate PDF portfolio statement.

        Returns:
            PDF as bytes
        """
        if generated_at is None:
            generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        html_content = self._generate_portfolio_html(holdings, metrics, generated_at)
        return self._html_to_pdf(html_content)

    def generate_sentiment_report(
        self, stocks: list[dict[str, object]], generated_at: str | None = None
    ) -> bytes:
        """Generate PDF sentiment analysis report.

        Returns:
            PDF as bytes
        """
        if generated_at is None:
            generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        html_content = self._generate_sentiment_html(stocks, generated_at)
        return self._html_to_pdf(html_content)

    def _generate_stock_html(
        self,
        symbol: str,
        name: str,
        price: float,
        change_pct: float,
        sentiment: str,
        summary: str,
        recommendation: str,
        catalysts: list[str],
        risks: list[str],
    ) -> str:
        """Generate HTML for stock report."""
        color = "#34d399" if change_pct > 0 else "#f87171"
        sent_color = (
            "#34d399" if sentiment == "Bullish" else "#f87171" if sentiment == "Bearish" else "#94a3b8"
        )

        catalysts_html = "".join(f"<li>{c}</li>" for c in catalysts)
        risks_html = "".join(f"<li>{r}</li>" for r in risks)

        return f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; line-height: 1.6; }}
                .header {{ background: #f8f9fa; padding: 20px; margin-bottom: 20px; border-radius: 8px; }}
                .symbol {{ font-size: 28px; font-weight: bold; margin-bottom: 10px; }}
                .price-info {{ display: flex; gap: 15px; align-items: center; }}
                .price {{ font-size: 24px; font-weight: bold; }}
                .change {{ color: {color}; font-weight: bold; }}
                .section {{ margin: 20px 0; padding: 15px; border-left: 4px solid #00d4aa; }}
                .section-title {{ font-size: 18px; font-weight: bold; color: #00d4aa; margin-bottom: 10px; }}
                .summary {{ color: #666; line-height: 1.8; }}
                .recommendation {{ background: #f0f9ff; padding: 15px; border-radius: 8px; color: #00d4aa; font-weight: bold; }}
                ul {{ margin: 10px 0; padding-left: 20px; }}
                li {{ margin: 8px 0; }}
                .sentiment {{ padding: 5px 10px; border-radius: 4px; background: rgba(0,212,170,0.1); color: {sent_color}; font-weight: bold; }}
                .footer {{ margin-top: 30px; padding-top: 15px; border-top: 1px solid #ddd; font-size: 12px; color: #999; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="symbol">{symbol}</div>
                <div>{name}</div>
                <div class="price-info">
                    <div class="price">₹{price:,.2f}</div>
                    <div class="change">{'+' if change_pct > 0 else ''}{change_pct:.2f}%</div>
                    <div class="sentiment">{sentiment}</div>
                </div>
            </div>

            <div class="section">
                <div class="section-title">Summary</div>
                <div class="summary">{summary}</div>
            </div>

            <div class="section">
                <div class="section-title">AI Recommendation</div>
                <div class="recommendation">{recommendation}</div>
            </div>

            <div class="section">
                <div class="section-title">Positive Catalysts</div>
                <ul>{catalysts_html}</ul>
            </div>

            <div class="section">
                <div class="section-title">Risk Factors</div>
                <ul>{risks_html}</ul>
            </div>

            <div class="footer">
                <p>Generated by IntelStock on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>This report is for informational purposes only and should not be considered investment advice.</p>
            </div>
        </body>
        </html>
        """

    def _generate_portfolio_html(
        self, holdings: list[dict[str, object]], metrics: dict[str, object], generated_at: str
    ) -> str:
        """Generate HTML for portfolio report."""
        holdings_html = ""
        for h in holdings:
            pnl_color = "#34d399" if h.get("gain_loss", 0) >= 0 else "#f87171"
            holdings_html += f"""
            <tr>
                <td>{h.get('symbol', '')}</td>
                <td>{h.get('quantity', '')}</td>
                <td>₹{h.get('avg_price', ''):,.2f}</td>
                <td>₹{h.get('current_price', ''):,.2f}</td>
                <td>₹{h.get('market_value', ''):,.2f}</td>
                <td style="color: {pnl_color};">₹{h.get('gain_loss', ''):,.2f}</td>
            </tr>
            """

        total_return = metrics.get("total_return_pct", 0)
        return_color = "#34d399" if total_return >= 0 else "#f87171"

        return f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; line-height: 1.6; }}
                .header {{ background: #f8f9fa; padding: 20px; margin-bottom: 20px; border-radius: 8px; }}
                .title {{ font-size: 24px; font-weight: bold; margin-bottom: 10px; }}
                .metrics {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px; }}
                .metric-box {{ background: #f0f9ff; padding: 15px; border-radius: 8px; }}
                .metric-label {{ font-size: 12px; color: #666; }}
                .metric-value {{ font-size: 20px; font-weight: bold; color: #00d4aa; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th {{ background: #f8f9fa; padding: 10px; text-align: left; border-bottom: 2px solid #ddd; }}
                td {{ padding: 10px; border-bottom: 1px solid #eee; }}
                .section {{ margin: 20px 0; }}
                .section-title {{ font-size: 18px; font-weight: bold; color: #00d4aa; margin-bottom: 10px; }}
                .footer {{ margin-top: 30px; padding-top: 15px; border-top: 1px solid #ddd; font-size: 12px; color: #999; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">Portfolio Statement</div>
                <div>Generated on {generated_at}</div>
            </div>

            <div class="metrics">
                <div class="metric-box">
                    <div class="metric-label">Total Value</div>
                    <div class="metric-value">₹{metrics.get('total_value', 0):,.2f}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Total Invested</div>
                    <div class="metric-value">₹{metrics.get('total_invested', 0):,.2f}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Gain/Loss</div>
                    <div class="metric-value">₹{metrics.get('total_gain_loss', 0):,.2f}</div>
                </div>
                <div class="metric-box">
                    <div class="metric-label">Return</div>
                    <div class="metric-value" style="color: {return_color};">{total_return:+.2f}%</div>
                </div>
            </div>

            <div class="section">
                <div class="section-title">Holdings</div>
                <table>
                    <thead>
                        <tr>
                            <th>Symbol</th>
                            <th>Quantity</th>
                            <th>Avg Price</th>
                            <th>Current Price</th>
                            <th>Market Value</th>
                            <th>Gain/Loss</th>
                        </tr>
                    </thead>
                    <tbody>
                        {holdings_html}
                    </tbody>
                </table>
            </div>

            <div class="footer">
                <p>This portfolio statement is for informational purposes only.</p>
            </div>
        </body>
        </html>
        """

    def _generate_sentiment_html(self, stocks: list[dict[str, object]], generated_at: str) -> str:
        """Generate HTML for sentiment report."""
        stocks_html = ""
        for s in stocks:
            sent_color = (
                "#34d399"
                if s.get("sentiment") == "Bullish"
                else "#f87171"
                if s.get("sentiment") == "Bearish"
                else "#94a3b8"
            )
            stocks_html += f"""
            <tr>
                <td>{s.get('symbol', '')}</td>
                <td>{s.get('name', '')}</td>
                <td style="color: {sent_color}; font-weight: bold;">{s.get('sentiment', '')}</td>
                <td>{s.get('confidence', 0):.2f}</td>
            </tr>
            """

        return f"""
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; line-height: 1.6; }}
                .header {{ background: #f8f9fa; padding: 20px; margin-bottom: 20px; border-radius: 8px; }}
                .title {{ font-size: 24px; font-weight: bold; margin-bottom: 10px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
                th {{ background: #f8f9fa; padding: 10px; text-align: left; border-bottom: 2px solid #ddd; }}
                td {{ padding: 10px; border-bottom: 1px solid #eee; }}
                .footer {{ margin-top: 30px; padding-top: 15px; border-top: 1px solid #ddd; font-size: 12px; color: #999; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="title">Market Sentiment Analysis</div>
                <div>Generated on {generated_at}</div>
            </div>

            <table>
                <thead>
                    <tr>
                        <th>Symbol</th>
                        <th>Company</th>
                        <th>Sentiment</th>
                        <th>Confidence</th>
                    </tr>
                </thead>
                <tbody>
                    {stocks_html}
                </tbody>
            </table>

            <div class="footer">
                <p>Sentiment analysis generated by IntelStock AI.</p>
            </div>
        </body>
        </html>
        """

    def _html_to_pdf(self, html_content: str) -> bytes:
        """Serve the report as HTML bytes.

        Extensible to real PDF rendering (e.g. weasyprint, reportlab) later.
        """
        return html_content.encode("utf-8")
