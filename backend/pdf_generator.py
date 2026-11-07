import io
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether,
    HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY

from database import IST_TZ, get_ist_now, format_timestamp_ist

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas that accumulates total page count and adds
    professional running headers (pages 2+) and running footers (all pages)
    with 'Page X of Y' and Asia/Kolkata (IST) generation metadata.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        page_w, page_h = A4

        # Header rule and title on pages 2 and onward
        if self._pageNumber > 1:
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#475569"))
            self.drawString(32, page_h - 24, "CodeAcharya")
            self.setFont("Helvetica", 8)
            self.drawString(88, page_h - 24, "•  Student Coding Performance Report  •  Asia/Kolkata (IST)")

            self.setStrokeColor(colors.HexColor("#cbd5e1"))
            self.setLineWidth(0.5)
            self.line(32, page_h - 28, page_w - 32, page_h - 28)

        # Footer on every page
        self.setStrokeColor(colors.HexColor("#e2e8f0"))
        self.setLineWidth(0.5)
        self.line(32, 28, page_w - 32, 28)

        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#64748b"))
        self.drawString(32, 17, "CodeAcharya Learning Platform  •  Confidential Student Performance Audit")
        
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(page_w - 32, 17, page_str)
        self.restoreState()


def generate_student_performance_pdf(
    data: Dict[str, Any],
    include_tab_switches: bool = True,
    include_viva: bool = True,
    view_mode: str = "detailed"
) -> bytes:
    """
    Generates a high-quality, professional, multi-page PDF performance report
    strictly adhering to CodeAcharya design principles, IST Asia/Kolkata timezone,
    and genuine database records without placeholders or mock statistics.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=32,
        rightMargin=32,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom typography matching CodeAcharya brand
    c_primary = colors.HexColor("#0f172a")     # Deep navy
    c_indigo = colors.HexColor("#4338ca")      # Brand indigo
    c_cyan = colors.HexColor("#0284c7")        # Cyan accent
    c_emerald = colors.HexColor("#059669")     # Green
    c_amber = colors.HexColor("#d97706")       # Amber
    c_red = colors.HexColor("#dc2626")         # Red
    c_muted = colors.HexColor("#64748b")       # Slate muted
    c_border = colors.HexColor("#cbd5e1")      # Border gray
    c_row_alt = colors.HexColor("#f8fafc")     # Table alt row

    h1_style = ParagraphStyle(
        "ReportH1",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=c_primary
    )

    h2_style = ParagraphStyle(
        "ReportH2",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=c_indigo,
        spaceBefore=14,
        spaceAfter=6
    )

    sub_style = ParagraphStyle(
        "ReportSub",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=12,
        textColor=c_cyan
    )

    meta_label_style = ParagraphStyle(
        "ReportMetaLabel",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#475569")
    )

    meta_val_style = ParagraphStyle(
        "ReportMetaVal",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=c_primary
    )

    tbl_header_style = ParagraphStyle(
        "TblHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9.5,
        textColor=colors.white,
        alignment=TA_LEFT
    )

    cell_style = ParagraphStyle(
        "TblCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7,
        leading=9,
        textColor=c_primary,
        alignment=TA_LEFT
    )

    cell_bold_style = ParagraphStyle(
        "TblCellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7,
        leading=9,
        textColor=c_primary,
        alignment=TA_LEFT
    )

    cell_muted_style = ParagraphStyle(
        "TblCellMuted",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=6.5,
        leading=8.5,
        textColor=c_muted,
        alignment=TA_LEFT
    )

    cell_badge_green = ParagraphStyle(
        "TblCellGreen",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7,
        leading=9,
        textColor=c_emerald
    )

    cell_badge_red = ParagraphStyle(
        "TblCellRed",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7,
        leading=9,
        textColor=c_red
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=12,
        textColor=colors.HexColor("#334155")
    )

    story = []

    user_info = data.get("user_info", {})
    summary = data.get("summary", {})
    questions_perf = data.get("questions_performance", [])
    tab_events = data.get("tab_switch_events", [])
    viva_sessions = data.get("viva_sessions", [])
    charts_data = data.get("charts", {})
    period_label = data.get("reporting_period_label", "Selected Period")

    now_ist_str = get_ist_now().strftime("%Y-%m-%d %H:%M:%S IST")

    # =========================================================================
    # A. REPORT HEADER
    # =========================================================================
    header_table_data = [
        [
            Paragraph("<b>CodeAcharya</b>", h1_style),
            Paragraph(f"<b>PERIOD:</b> {period_label}", ParagraphStyle("PeriodR", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=c_indigo, alignment=TA_RIGHT))
        ],
        [
            Paragraph("STUDENT CODING PERFORMANCE &amp; PEDAGOGICAL AUDIT REPORT", sub_style),
            Paragraph(f"<b>Generated:</b> {now_ist_str}", ParagraphStyle("GenR", parent=styles["Normal"], fontName="Helvetica", fontSize=8, leading=10, textColor=c_muted, alignment=TA_RIGHT))
        ]
    ]
    h_table = Table(header_table_data, colWidths=[331, 200])
    h_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0)
    ]))
    story.append(h_table)
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width="100%", thickness=1.5, color=c_indigo, spaceBefore=0, spaceAfter=8))

    # Student metadata card
    student_meta_data = [
        [
            Paragraph("Student Name:", meta_label_style),
            Paragraph(user_info.get("full_name", "Student Learner"), meta_val_style),
            Paragraph("Account Email / ID:", meta_label_style),
            Paragraph(user_info.get("email", "student@codeacharya.internal"), meta_val_style)
        ],
        [
            Paragraph("Timezone Standard:", meta_label_style),
            Paragraph("Asia/Kolkata (IST, UTC+05:30)", meta_val_style),
            Paragraph("Evaluation Engine:", meta_label_style),
            Paragraph("CodeAcharya Automated &amp; AST Verifier", meta_val_style)
        ]
    ]
    meta_table = Table(student_meta_data, colWidths=[90, 175, 105, 161])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
        ("BOX", (0, 0), (-1, -1), 0.5, c_border),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6)
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 12))

    # =========================================================================
    # B. PERFORMANCE SUMMARY
    # =========================================================================
    story.append(Paragraph("1. Executive Performance Summary", h2_style))

    # Format values safely with transparent labeling and N/A handling
    avg_score_val = summary.get("average_coding_score")
    avg_score_disp = f"{avg_score_val:.1f} / 100" if avg_score_val is not None else "N/A"

    best_score_val = summary.get("best_coding_score")
    best_score_disp = f"{best_score_val:.1f} / 100" if best_score_val is not None else "N/A"

    pass_rate_val = summary.get("overall_pass_rate_percentage")
    tests_eval = summary.get("total_test_cases_evaluated", 0)
    tests_pass = summary.get("total_test_cases_passed", 0)
    if tests_eval > 0 and pass_rate_val is not None:
        pass_rate_disp = f"{pass_rate_val:.1f}% ({tests_pass}/{tests_eval})"
    else:
        pass_rate_disp = "N/A"

    viva_val = summary.get("viva", {}).get("average_score")
    viva_cnt = summary.get("viva", {}).get("sessions_count", 0)
    if viva_val is not None and viva_cnt > 0:
        viva_summary_disp = f"{viva_val:.1f} / 100 ({viva_cnt} session{'s' if viva_cnt != 1 else ''})"
    else:
        viva_summary_disp = "N/A"

    completed_cnt = summary.get("completed_attempts", 0)
    failed_cnt = summary.get("failed_attempts", 0)
    abandoned_cnt = summary.get("abandoned_attempts", 0)
    running_cnt = summary.get("running_attempts", 0)
    paused_cnt = summary.get("paused_attempts", 0)

    status_parts = [
        f"{completed_cnt} completed",
        f"{failed_cnt} failed",
        f"{abandoned_cnt} abandoned"
    ]
    if running_cnt > 0:
        status_parts.append(f"{running_cnt} running")
    if paused_cnt > 0:
        status_parts.append(f"{paused_cnt} paused")
    activity_status_disp = ", ".join(status_parts)

    avg_time_comp = summary.get("avg_coding_time_completed_formatted", "0s")
    if completed_cnt == 0:
        avg_time_comp = "N/A"

    summary_grid_data = [
        [
            Paragraph("<b>Unique Questions Solved:</b>", meta_label_style),
            Paragraph(f"<b>{summary.get('total_unique_solved', 0)}</b>", meta_val_style),
            Paragraph("<b>Total Coding Attempts:</b>", meta_label_style),
            Paragraph(f"<b>{summary.get('total_attempts', 0)}</b> ({completed_cnt} completed)", meta_val_style)
        ],
        [
            Paragraph("<b>Average Coding Score:</b><br/><font size='6' color='#64748b'>(All evaluated attempts)</font>", meta_label_style),
            Paragraph(f"<b>{avg_score_disp}</b>", meta_val_style),
            Paragraph("<b>Best Coding Score:</b><br/><font size='6' color='#64748b'>(Highest single attempt)</font>", meta_label_style),
            Paragraph(f"<b>{best_score_disp}</b>", meta_val_style)
        ],
        [
            Paragraph("<b>Total Active Coding Time:</b>", meta_label_style),
            Paragraph(summary.get("total_active_coding_time_formatted", "0s"), meta_val_style),
            Paragraph("<b>Avg Time / Solved Question:</b>", meta_label_style),
            Paragraph(avg_time_comp, meta_val_style)
        ],
        [
            Paragraph("<b>Total Unique Hints Used:</b>", meta_label_style),
            Paragraph(f"{summary.get('total_unique_hints_used', 0)} revealed", meta_val_style),
            Paragraph("<b>Overall Test Pass Rate:</b>", meta_label_style),
            Paragraph(f"<b>{pass_rate_disp}</b>", meta_val_style)
        ],
        [
            Paragraph("<b>Total Tab Switches:</b>", meta_label_style),
            Paragraph(f"{summary.get('total_tab_switches', 0)} events", meta_val_style),
            Paragraph("<b>Total Time Away from Page:</b>", meta_label_style),
            Paragraph(summary.get("total_time_away_formatted", "0s"), meta_val_style)
        ],
        [
            Paragraph("<b>AI Viva Performance:</b>", meta_label_style),
            Paragraph(viva_summary_disp, meta_val_style),
            Paragraph("<b>Activity Status:</b>", meta_label_style),
            Paragraph(activity_status_disp, meta_val_style)
        ]
    ]

    sum_table = Table(summary_grid_data, colWidths=[120, 145, 120, 146])
    sum_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.white),
        ("BOX", (0, 0), (-1, -1), 1, c_border),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, c_row_alt])
    ]))
    story.append(sum_table)
    story.append(Spacer(1, 14))

    # =========================================================================
    # C. QUESTION-WISE PERFORMANCE
    # =========================================================================
    story.append(Paragraph(f"2. Question-Wise Coding Performance ({len(questions_perf)} recorded attempts)", h2_style))

    if not questions_perf:
        story.append(Paragraph("<i>No coding attempts recorded in the selected period.</i>", cell_muted_style))
        story.append(Spacer(1, 10))
    else:
        # Table columns:
        # 1. Question Title & Stable ID (105 pt)
        # 2. Topic & Difficulty (75 pt)
        # 3. Lang & Attempt # (48 pt)
        # 4. Status (48 pt)
        # 5. Timestamps IST (80 pt)
        # 6. Coding / Exec Time (55 pt)
        # 7. Tests & Score (60 pt)
        # 8. Hints & Tab Switches (60 pt)
        # Total = 105 + 75 + 48 + 48 + 80 + 55 + 60 + 60 = 531 pt
        q_table_data = [
            [
                Paragraph("<b>Question &amp; ID</b>", tbl_header_style),
                Paragraph("<b>Topic &amp; Diff</b>", tbl_header_style),
                Paragraph("<b>Lang / #</b>", tbl_header_style),
                Paragraph("<b>Status</b>", tbl_header_style),
                Paragraph("<b>Timestamps (IST)</b>", tbl_header_style),
                Paragraph("<b>Duration</b>", tbl_header_style),
                Paragraph("<b>Score / Tests</b>", tbl_header_style),
                Paragraph("<b>Hints &amp; Away</b>", tbl_header_style)
            ]
        ]

        for att in questions_perf:
            # Status badge
            stat_name = (att.get("attempt_status") or "completed").lower().strip()
            if stat_name == "completed" or att.get("is_completed"):
                stat_p = Paragraph("<font color='#059669'><b>Completed</b></font>", cell_badge_green)
            elif stat_name == "failed":
                stat_p = Paragraph("<font color='#dc2626'><b>Failed</b></font>", cell_badge_red)
            elif stat_name == "abandoned":
                stat_p = Paragraph("<font color='#d97706'><b>Abandoned</b></font>", cell_style)
            elif stat_name == "running":
                stat_p = Paragraph("<font color='#0284c7'><b>Running</b></font>", cell_style)
            elif stat_name == "paused":
                stat_p = Paragraph("<font color='#475569'><b>Paused</b></font>", cell_style)
            else:
                stat_p = Paragraph(f"<b>{stat_name.capitalize()}</b>", cell_style)

            # Score representation
            sc_val = att.get("overall_score")
            is_prov = att.get("is_provisional", False)
            if sc_val is not None:
                if is_prov:
                    sc_text = f"<b>{sc_val:.1f}</b>/100<br/><font size='5' color='#d97706'><b>(Provisional)</b></font>"
                else:
                    sc_text = f"<b>{sc_val:.1f}</b>/100"
            else:
                sc_text = "<i>N/A</i>"
            tot_tests = att.get("total_count", 0)
            if tot_tests > 0:
                test_text = f"{att.get('passed_count', 0)}/{tot_tests} tests"
            else:
                test_text = "N/A (0 tests)"

            # Coding time & execution time
            c_dur = att.get("coding_duration_formatted", "00:00")
            e_ms = att.get("execution_time_ms")
            e_text = f"{e_ms:.1f}ms" if e_ms is not None else "N/A"

            # Hints & away
            h_used = att.get("unique_hints_used", 0)
            indep_sc = att.get("independent_score", 10.0)
            switches = att.get("tab_switch_count", 0)
            away_str = att.get("time_away_formatted", "0s")

            start_disp = att.get("start_time_ist") or "N/A"
            end_disp = att.get("end_time_ist") or "In progress"

            q_table_data.append([
                Paragraph(
                    f"<b>{att.get('question_title', 'Untitled')}</b><br/>"
                    f"<font color='#64748b' size='6'>{att.get('question_id', '')}</font>",
                    cell_style
                ),
                Paragraph(
                    f"{att.get('topic', 'General')}<br/>"
                    f"<font color='#475569' size='6'><b>{att.get('difficulty', 'Medium')}</b></font>",
                    cell_style
                ),
                Paragraph(
                    f"{att.get('language', 'py').upper()}<br/>"
                    f"<font color='#64748b'>Att #{att.get('attempt_number', 1)}</font>",
                    cell_style
                ),
                stat_p,
                Paragraph(
                    f"<font size='6'><b>Start:</b> {start_disp}</font><br/>"
                    f"<font size='6' color='#64748b'><b>End:</b> {end_disp}</font>",
                    cell_style
                ),
                Paragraph(
                    f"<b>Code:</b> {c_dur}<br/>"
                    f"<font size='6' color='#64748b'><b>Exec:</b> {e_text}</font>",
                    cell_style
                ),
                Paragraph(
                    f"{sc_text}<br/>"
                    f"<font size='6' color='#64748b'>{test_text}</font>",
                    cell_style
                ),
                Paragraph(
                    f"Hints: {h_used} ({indep_sc:.0f}/10)<br/>"
                    f"<font size='6' color='#64748b'>Tabs: {switches} ({away_str})</font>",
                    cell_style
                )
            ])

        q_table = Table(
            q_table_data,
            colWidths=[105, 75, 48, 48, 80, 55, 60, 60],
            repeatRows=1
        )
        q_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("BOX", (0, 0), (-1, -1), 0.5, c_border),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, c_row_alt]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
        ]))
        story.append(q_table)
        story.append(Spacer(1, 14))

    # =========================================================================
    # D. TAB-SWITCH HISTORY (OPTIONAL SECTION)
    # =========================================================================
    if include_tab_switches:
        story.append(Paragraph(f"3. Tab-Switch &amp; Page Visibility Activity ({len(tab_events)} recorded events)", h2_style))
        story.append(Paragraph(
            "<i>Activity telemetry logs browser visibility events (Page Visibility API) to track focus patterns and duration away from the active coding IDE.</i>",
            cell_muted_style
        ))
        story.append(Spacer(1, 4))

        if not tab_events:
            story.append(Paragraph("<i>No browser focus/tab-switch events recorded in the selected period.</i>", cell_muted_style))
            story.append(Spacer(1, 10))
        else:
            # Columns: Switch # (40 pt), Question / Context (120 pt), Date (65 pt), Hidden IST (110 pt), Return IST (110 pt), Away / Status (86 pt)
            # Total = 40 + 120 + 65 + 110 + 110 + 86 = 531 pt
            ts_table_data = [
                [
                    Paragraph("<b>#</b>", tbl_header_style),
                    Paragraph("<b>Question Context</b>", tbl_header_style),
                    Paragraph("<b>Date (IST)</b>", tbl_header_style),
                    Paragraph("<b>Page Hidden (IST)</b>", tbl_header_style),
                    Paragraph("<b>Returned (IST)</b>", tbl_header_style),
                    Paragraph("<b>Duration Away / Status</b>", tbl_header_style)
                ]
            ]

            for ev in tab_events:
                is_incomplete = ev.get("status") in ("incomplete", "away", "active") or "Awaiting" in str(ev.get("return_time_ist", "")) or "Pending" in str(ev.get("return_time_ist", ""))
                is_unrec = ev.get("status") == "historical_unrecorded" or ev.get("is_unrecorded") or ev.get("duration_away_formatted") == "N/A"
                if is_unrec:
                    status_color = "#64748b"
                    status_label = "Unrecorded (Legacy)"
                    dur_display = "N/A"
                elif is_incomplete:
                    status_color = "#d97706"
                    status_label = "Awaiting return"
                    dur_display = ev.get("duration_away_formatted") or "Incomplete"
                else:
                    status_color = "#059669"
                    status_label = "Returned"
                    dur_display = ev.get("duration_away_formatted", "0s")

                ts_table_data.append([
                    Paragraph(str(ev.get("switch_number", "")), cell_style),
                    Paragraph(
                        f"<b>{ev.get('question_title', 'General IDE')}</b><br/>"
                        f"<font size='6' color='#64748b'>{ev.get('attempt_id', '')}</font>",
                        cell_style
                    ),
                    Paragraph(ev.get("date_ist", "N/A"), cell_style),
                    Paragraph(ev.get("hidden_time_ist", "N/A"), cell_style),
                    Paragraph(ev.get("return_time_ist", "N/A"), cell_style),
                    Paragraph(
                        f"<b>{dur_display}</b><br/>"
                        f"<font size='6' color='{status_color}'><b>{status_label}</b></font>",
                        cell_style
                    )
                ])

            ts_table = Table(
                ts_table_data,
                colWidths=[40, 120, 65, 110, 110, 86],
                repeatRows=1
            )
            ts_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334155")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.5, c_border),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, c_row_alt]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
            ]))
            story.append(ts_table)
            story.append(Spacer(1, 14))

    # =========================================================================
    # E. AI VIVA RESULTS (OPTIONAL SECTION)
    # =========================================================================
    if include_viva:
        story.append(Paragraph(f"4. AI Viva Oral Defense Evaluations ({len(viva_sessions)} sessions)", h2_style))

        if not viva_sessions:
            story.append(Paragraph("<i>No AI Viva defense sessions recorded in the selected period.</i>", cell_muted_style))
            story.append(Spacer(1, 10))
        else:
            # Columns: Date IST (75 pt), Question (110 pt), Score (45 pt), Dimensions (120 pt), Feedback (181 pt)
            # Total = 75 + 110 + 45 + 120 + 181 = 531 pt
            viva_table_data = [
                [
                    Paragraph("<b>Session Date (IST)</b>", tbl_header_style),
                    Paragraph("<b>Question</b>", tbl_header_style),
                    Paragraph("<b>Score</b>", tbl_header_style),
                    Paragraph("<b>Dimension Breakdown</b>", tbl_header_style),
                    Paragraph("<b>Examiner Feedback Summary</b>", tbl_header_style)
                ]
            ]

            for vs in viva_sessions:
                concept_s = vs.get("conceptual_score", "N/A")
                code_s = vs.get("code_understanding_score", "N/A")
                comp_s = vs.get("complexity_score", "N/A")
                comm_s = vs.get("communication_score", "N/A")

                viva_table_data.append([
                    Paragraph(vs.get("completed_at_ist", "N/A"), cell_style),
                    Paragraph(f"<b>{vs.get('question_title', 'Coding Question')}</b>", cell_style),
                    Paragraph(f"<b>{vs.get('overall_score', 0)}/100</b>", cell_bold_style),
                    Paragraph(
                        f"Concept: {concept_s} • Code: {code_s}<br/>"
                        f"Complexity: {comp_s} • Comm: {comm_s}",
                        cell_style
                    ),
                    Paragraph(vs.get("feedback_summary", "Evaluation completed successfully."), cell_style)
                ])

            viva_table = Table(
                viva_table_data,
                colWidths=[75, 110, 45, 120, 181],
                repeatRows=1
            )
            viva_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4c1d95")), # Royal purple
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.5, c_border),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, c_row_alt]),
                ("VALIGN", (0, 0), (-1, -1), "TOP")
            ]))
            story.append(viva_table)
            story.append(Spacer(1, 14))

    # =========================================================================
    # F. PERFORMANCE INSIGHTS & PEDAGOGICAL AUDIT
    # =========================================================================
    story.append(Paragraph("5. Grounded Pedagogical Insights &amp; Improvement Plan", h2_style))

    # Compile data-grounded insights
    insights = []
    
    # 1. Hint independence analysis
    total_hints = summary.get("total_unique_hints_used", 0)
    att_count = summary.get("total_attempts", 0)
    avg_hints = round(total_hints / max(1, att_count), 1)
    if total_hints == 0 and att_count > 0:
        insights.append(
            "<b>Exceptional Problem-Solving Independence:</b> Zero progressive hints were unlocked during this period. "
            "Full 10/10 points were retained across all Independent Problem-Solving scoring components."
        )
    elif avg_hints <= 1.0:
        insights.append(
            f"<b>Strong Independent Formulation:</b> Averaged {avg_hints} hint per attempt. "
            "Most solutions relied on self-driven debugging with minimal hint penalties."
        )
    else:
        insights.append(
            f"<b>Hint Dependency Observed:</b> Averaged {avg_hints} hints per coding problem. "
            "To maximize your score out of 100, try sketching algorithmic invariants and dry-running small examples on paper before opening progressive hints."
        )

    # 2. Topic performance analysis (Grounded recommendations per topic domain)
    topic_acc = charts_data.get("topic_accuracy", [])
    if topic_acc:
        sorted_topics = sorted(topic_acc, key=lambda x: x.get("pass_rate_percentage", 0), reverse=True)
        strongest = sorted_topics[0]
        weakest = sorted_topics[-1]
        insights.append(
            f"<b>Strongest Topic:</b> {strongest['topic']} with {strongest['pass_rate_percentage']:.1f}% pass rate and {strongest.get('average_score', 0):.1f}/100 average score across {strongest['attempts_count']} attempt(s)."
        )
        if len(sorted_topics) > 1 and weakest["topic"] != strongest["topic"]:
            w_top = str(weakest.get("topic", "")).lower()
            if "recursion" in w_top:
                target_advice = "base case validation, call stack depth limits, and recurrence invariants."
            elif "tree" in w_top or "graph" in w_top:
                target_advice = "visited state tracking, empty tree edge cases, and traversal termination."
            elif "dp" in w_top or "dynamic" in w_top:
                target_advice = "overlapping subproblem memoization, state transition bounds, and base initialization."
            elif "array" in w_top or "string" in w_top:
                target_advice = "off-by-one index guards, loop termination bounds, and empty input checks."
            elif "list" in w_top:
                target_advice = "pointer reassignment ordering, null head checks, and single-element bounds."
            else:
                target_advice = "targeted test-case verification and constraint boundary analysis."

            insights.append(
                f"<b>Target Growth Area:</b> {weakest['topic']} demonstrated a {weakest['pass_rate_percentage']:.1f}% pass rate. Recommend targeted practice on {target_advice}"
            )

    # 3. Focus and time efficiency (Presented neutrally as recorded activity telemetry)
    switches = summary.get("total_tab_switches", 0)
    t_away_fmt = summary.get("total_time_away_formatted", "0s")
    all_unrec = (switches > 0 and all(ev.get("is_unrecorded") or ev.get("status") == "historical_unrecorded" for ev in tab_events))
    if switches == 0:
        insights.append("<b>Browser Focus Telemetry:</b> Continuous IDE focus maintained with 0 tab switch events recorded across all coding sessions.")
    elif all_unrec:
        insights.append(
            f"<b>Browser Focus &amp; Navigation Activity:</b> {switches} tab switch event(s) recorded in audit history. Historical events reflect legacy telemetry without reliable persisted durations; real-time duration tracking is active for current sessions."
        )
    else:
        insights.append(
            f"<b>Browser Focus &amp; Navigation Activity:</b> {switches} tab switch event(s) recorded with {t_away_fmt} cumulative duration away from active IDE."
        )

    # 4. Viva alignment
    if viva_sessions:
        avg_v = summary.get("viva", {}).get("average_score", 0)
        if avg_v >= 80:
            insights.append(f"<b>Superb Oral Articulation:</b> AI Viva average of {avg_v:.1f}/100 demonstrates high mastery in articulating asymptotic complexities and code trade-offs.")
        else:
            insights.append(f"<b>Oral Defense Practice:</b> AI Viva average of {avg_v:.1f}/100. Practice verbalizing Big-O justifications and space trade-offs clearly.")
    else:
        insights.append("<b>Oral Defense Step:</b> No AI Viva sessions were conducted in this period. Take completed coding problems into the AI Viva Room to validate conceptual understanding.")

    # Render insights box
    insights_html = "<br/><br/>".join([f"•  {item}" for item in insights])
    insight_p = Paragraph(insights_html, body_style)

    box_table = Table([[insight_p]], colWidths=[531])
    box_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#cbd5e1")),
        ("LINELEFT", (0, 0), (0, 0), 3, c_indigo),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10)
    ]))
    story.append(box_table)

    # Build PDF with multi-pass NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    return buf.getvalue()

generate_pdf_report = generate_student_performance_pdf
