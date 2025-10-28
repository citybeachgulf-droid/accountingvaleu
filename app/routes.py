from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
from . import db
from .models import Branch, Client, ValuationReport
from datetime import date
from openpyxl import Workbook
from io import BytesIO

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    branch_id = request.args.get('branch', type=int)

    branches = Branch.query.order_by(Branch.name).all()

    if branch_id:
        # filter reports to selected branch
        reports = (
            ValuationReport.query
            .join(Client)
            .filter(Client.branch_id == branch_id)
            .order_by(ValuationReport.date.desc())
            .all()
        )
    else:
        reports = ValuationReport.query.order_by(ValuationReport.date.desc()).all()

    # compute total
    total = sum(r.amount or 0 for r in reports)

    return render_template('reports.html', reports=reports, branches=branches, selected_branch=branch_id, total=total)

@bp.route('/add_report', methods=['GET', 'POST'])
def add_report():
    branches = Branch.query.order_by(Branch.name).all()
    if request.method == 'POST':
        client_name = request.form.get('client_name', '').strip()
        client_phone = request.form.get('client_phone', '').strip()
        report_number = request.form.get('report_number', '').strip()
        amount = request.form.get('amount')
        note = request.form.get('note')
        branch_id = int(request.form.get('branch_id'))

        # ensure amount
        try:
            amount = float(amount)
        except Exception:
            amount = 0.0

        # check if client exists in the same branch (by name and phone)
        client = Client.query.filter_by(name=client_name, phone=client_phone, branch_id=branch_id).first()
        if not client:
            # create automatically
            client = Client(name=client_name or 'عميل بدون اسم', phone=client_phone, branch_id=branch_id)
            db.session.add(client)
            db.session.commit()

        # create report
        report = ValuationReport(report_number=report_number or 'N/A', client_id=client.id, amount=amount, date=date.today(), note=note)
        db.session.add(report)
        db.session.commit()

        flash('تم حفظ التقرير بنجاح', 'success')
        return redirect(url_for('main.index'))

    return render_template('add_report.html', branches=branches)

@bp.route('/export_excel')
def export_excel():
    branch_id = request.args.get('branch', type=int)
    if branch_id:
        reports = (
            ValuationReport.query
            .join(Client)
            .filter(Client.branch_id == branch_id)
            .order_by(ValuationReport.date.desc())
            .all()
        )
    else:
        reports = ValuationReport.query.order_by(ValuationReport.date.desc()).all()

    wb = Workbook()
    ws = wb.active
    ws.title = 'Reports'

    headers = ['اسم العميل', 'رقم الهاتف', 'رقم التقرير', 'المبلغ', 'الفرع', 'التاريخ', 'ملاحظات']
    ws.append(headers)

    for r in reports:
        ws.append([
            r.client.name,
            r.client.phone,
            r.report_number,
            r.amount,
            r.client.branch.name if r.client.branch else '',
            r.date.strftime('%Y-%m-%d'),
            r.note or ''
        ])

    stream = BytesIO()
    wb.save(stream)
    stream.seek(0)

    filename = 'valuation_reports.xlsx'
    return send_file(stream, as_attachment=True, download_name=filename, mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
