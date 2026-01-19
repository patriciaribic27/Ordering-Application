"""
PDF Exporter for order reports.
Enables export of daily reports in PDF format using reportlab.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime
from pathlib import Path
from typing import List
from services.order_service import Order, OrderStatus


class PDFExporter:
    """Exporter for PDF format reports."""
    
    def __init__(self, export_dir: str = "izvjestaji"):
        """
        Initialize PDF exporter.
        
        Args:
            export_dir: Directory where reports will be saved
        """
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(exist_ok=True)
        
        # Define styles
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        self.normal_style = self.styles['Normal']
    
    def export_daily_report(self, orders: List[Order]) -> str:
        """
        Export daily report with statistics to PDF.
        
        Args:
            orders: List of all orders
            
        Returns:
            Full path to created file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"daily_report_{timestamp}.pdf"
        filepath = self.export_dir / filename
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(filepath),
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Container for PDF elements
        story = []
        
        # Title
        title = Paragraph("☕ DAILY ORDER REPORT", self.title_style)
        story.append(title)
        story.append(Spacer(1, 12))
        
        # Date and time information
        date_info = f"<b>Date:</b> {datetime.now().strftime('%Y-%m-%d')}<br/>"
        date_info += f"<b>Generated:</b> {datetime.now().strftime('%H:%M:%S')}"
        story.append(Paragraph(date_info, self.normal_style))
        story.append(Spacer(1, 20))
        
        # Calculate statistics
        total_orders = len(orders)
        completed_orders = len([o for o in orders if o.status == OrderStatus.COMPLETED])
        cancelled_orders = len([o for o in orders if o.status == OrderStatus.CANCELLED])
        total_revenue = sum(o.price for o in orders if o.status == OrderStatus.COMPLETED)
        
        # Overall statistics section
        story.append(Paragraph("📊 OVERALL STATISTICS", self.heading_style))
        
        stats_data = [
            ['Metric', 'Value'],
            ['Total Orders', str(total_orders)],
            ['Completed Orders', str(completed_orders)],
            ['Cancelled Orders', str(cancelled_orders)],
            ['Total Revenue', f'{total_revenue:.2f} EUR']
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#34495e')),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#ecf0f1')])
        ]))
        
        story.append(stats_table)
        story.append(Spacer(1, 20))
        
        # Statistics per beverage
        story.append(Paragraph("🍹 STATISTICS PER BEVERAGE", self.heading_style))
        
        beverage_stats = {}
        for order in orders:
            if order.beverage_name not in beverage_stats:
                beverage_stats[order.beverage_name] = {
                    'quantity': 0,
                    'revenue': 0.0,
                    'count': 0
                }
            beverage_stats[order.beverage_name]['count'] += 1
            beverage_stats[order.beverage_name]['quantity'] += order.quantity
            if order.status == OrderStatus.COMPLETED:
                beverage_stats[order.beverage_name]['revenue'] += order.price
        
        beverage_data = [['Beverage', 'Orders', 'Quantity', 'Revenue (EUR)']]
        
        for beverage, stats in sorted(beverage_stats.items(), 
                                     key=lambda x: x[1]['revenue'], 
                                     reverse=True):
            beverage_data.append([
                beverage,
                str(stats['count']),
                str(stats['quantity']),
                f"{stats['revenue']:.2f}"
            ])
        
        beverage_table = Table(beverage_data, colWidths=[2*inch, 1.2*inch, 1.2*inch, 1.4*inch])
        beverage_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#34495e')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#d5f4e6')])
        ]))
        
        story.append(beverage_table)
        story.append(Spacer(1, 20))
        
        # Detailed orders section
        story.append(Paragraph("📋 DETAILED ORDERS", self.heading_style))
        
        order_data = [['ID', 'Beverage', 'Qty', 'Price', 'Status', 'Time', 'Duration']]
        
        for order in sorted(orders, key=lambda x: x.created_at):
            duration = ""
            if order.completed_at:
                duration = f"{(order.completed_at - order.created_at).total_seconds():.1f}s"
            
            # Color code by status
            status_text = order.status.value.upper()
            
            order_data.append([
                order.id[:8],  # Shortened ID
                order.beverage_name,
                str(order.quantity),
                f"{order.price:.2f}€",
                status_text,
                order.created_at.strftime("%H:%M:%S"),
                duration
            ])
        
        order_table = Table(order_data, colWidths=[0.8*inch, 1.3*inch, 0.5*inch, 0.8*inch, 1*inch, 0.9*inch, 0.9*inch])
        
        # Base table style
        table_style = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
        ]
        
        # Color rows by status
        for i, order in enumerate(sorted(orders, key=lambda x: x.created_at), start=1):
            if order.status == OrderStatus.COMPLETED:
                table_style.append(('BACKGROUND', (4, i), (4, i), colors.HexColor('#d4edda')))
            elif order.status == OrderStatus.CANCELLED:
                table_style.append(('BACKGROUND', (4, i), (4, i), colors.HexColor('#f8d7da')))
            elif order.status == OrderStatus.PROCESSING:
                table_style.append(('BACKGROUND', (4, i), (4, i), colors.HexColor('#cce5ff')))
            elif order.status == OrderStatus.READY:
                table_style.append(('BACKGROUND', (4, i), (4, i), colors.HexColor('#d1ecf1')))
        
        order_table.setStyle(TableStyle(table_style))
        story.append(order_table)
        
        # Footer
        story.append(Spacer(1, 30))
        footer_text = f"<i>Generated by Modern Ordering Application • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</i>"
        footer = Paragraph(footer_text, ParagraphStyle('Footer', parent=self.normal_style, fontSize=8, textColor=colors.grey, alignment=TA_CENTER))
        story.append(footer)
        
        # Build PDF
        doc.build(story)
        
        return str(filepath)
    
    def export_summary(self, orders: List[Order]) -> str:
        """
        Export summary report with statistics only (no detailed orders).
        
        Args:
            orders: List of all orders
            
        Returns:
            Full path to created file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"summary_report_{timestamp}.pdf"
        filepath = self.export_dir / filename
        
        doc = SimpleDocTemplate(str(filepath), pagesize=letter)
        story = []
        
        # Title
        title = Paragraph("📊 SUMMARY REPORT", self.title_style)
        story.append(title)
        story.append(Spacer(1, 20))
        
        # Calculate statistics
        total_orders = len(orders)
        completed_orders = len([o for o in orders if o.status == OrderStatus.COMPLETED])
        cancelled_orders = len([o for o in orders if o.status == OrderStatus.CANCELLED])
        total_revenue = sum(o.price for o in orders if o.status == OrderStatus.COMPLETED)
        
        # Statistics
        stats_data = [
            ['Metric', 'Value'],
            ['Total Orders', str(total_orders)],
            ['Completed Orders', str(completed_orders)],
            ['Cancelled Orders', str(cancelled_orders)],
            ['Total Revenue', f'{total_revenue:.2f} EUR']
        ]
        
        stats_table = Table(stats_data, colWidths=[3*inch, 2*inch])
        stats_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        story.append(stats_table)
        doc.build(story)
        
        return str(filepath)
