import { jsPDF } from 'jspdf';

export function exportQuestionsToPdf(questions, notes = {}, meta = {}, context = null) {
  const doc = new jsPDF({ unit: 'pt', format: 'a4' });
  const margin = 48;
  const pageWidth = doc.internal.pageSize.getWidth();
  const maxWidth = pageWidth - margin * 2;
  let y = margin;

  const addLine = (text, fontSize = 11, bold = false) => {
    doc.setFont('helvetica', bold ? 'bold' : 'normal');
    doc.setFontSize(fontSize);
    const lines = doc.splitTextToSize(text, maxWidth);
    for (const line of lines) {
      if (y > doc.internal.pageSize.getHeight() - margin) {
        doc.addPage();
        y = margin;
      }
      doc.text(line, margin, y);
      y += fontSize + 6;
    }
  };

  addLine('Interview Intelligence — Question Set', 18, true);
  y += 8;
  if (meta.qualityScore) {
    addLine(`Quality score: ${(meta.qualityScore * 100).toFixed(0)}%`, 10);
  }
  y += 12;

  if (context) {
    if (context.jd_explanation_for_hr || context.jd_summary) {
      addLine("Role Expectation Overview", 13, true);
      addLine(context.jd_explanation_for_hr || context.jd_summary, 10);
      y += 8;
    }

    if (context.experience_level) {
      addLine(`Role Seniority Level: ${context.experience_level}`, 10, true);
      y += 8;
    }

    if (context.extracted_skills_with_levels && context.extracted_skills_with_levels.length > 0) {
      addLine('Required Skills', 13, true);
      const skillsText = context.extracted_skills_with_levels
        .map(item => item.skill)
        .join(', ');
      addLine(skillsText, 10);
      y += 8;
    }

    if (context.self_rating_questions && context.self_rating_questions.length > 0) {
      addLine('Core Skill Questions', 13, true);
      context.self_rating_questions.forEach((q, idx) => {
        addLine(`${idx + 1}. ${q}`, 10);
      });
      y += 12;
    }

    addLine('----------------------------------------------------------------------------------------------------', 10);
    y += 12;
  }

  questions.forEach((q, i) => {
    addLine(`Question ${i + 1}${q.category === 'scenario' ? ' (Scenario)' : ''}`, 13, true);
    addLine(q.question, 11);
    addLine(`Difficulty: ${q.difficulty}  |  Technology: ${q.related_technology}`, 10);
    addLine(`Explanation: ${q.explanation}`, 10);
    if (q.answer) {
      addLine(`Answer: ${q.answer}`, 10);
    }
    if (notes[i]) {
      addLine(`Recruiter notes: ${notes[i]}`, 10);
    }
    y += 16;
  });

  doc.save('interview-questions.pdf');
}

export function exportJdAnalysisToPdf(context) {
  if (!context) return;
  const doc = new jsPDF({ unit: 'pt', format: 'a4' });
  const margin = 48;
  const pageWidth = doc.internal.pageSize.getWidth();
  const maxWidth = pageWidth - margin * 2;
  let y = margin;

  const addLine = (text, fontSize = 11, bold = false, color = '#141414') => {
    doc.setFont('helvetica', bold ? 'bold' : 'normal');
    doc.setFontSize(fontSize);
    doc.setTextColor(color);
    const lines = doc.splitTextToSize(text, maxWidth);
    for (const line of lines) {
      if (y > doc.internal.pageSize.getHeight() - margin) {
        doc.addPage();
        y = margin;
      }
      doc.text(line, margin, y);
      y += fontSize + 6;
    }
  };

  addLine('Interview Intelligence', 10, true, '#2d6a4f');
  y += 4;
  addLine('Job Description Analysis Report', 20, true);
  y += 15;

  if (context.jd_explanation_for_hr || context.jd_summary) {
    addLine('Role Expectation Overview', 14, true, '#2d6a4f');
    y += 4;
    addLine(context.jd_explanation_for_hr || context.jd_summary, 10);
    y += 12;
  }

  if (context.experience_level) {
    addLine('Role Seniority Level', 14, true, '#2d6a4f');
    y += 4;
    addLine(context.experience_level, 10);
    y += 12;
  }

  if (context.extracted_skills_with_levels && context.extracted_skills_with_levels.length > 0) {
    addLine('Required Skills Baseline', 14, true, '#2d6a4f');
    y += 4;
    const skillsText = context.extracted_skills_with_levels
      .map(item => item.skill)
      .join(', ');
    addLine(skillsText, 10);
    y += 12;
  }

  if (context.self_rating_questions && context.self_rating_questions.length > 0) {
    addLine('Recruiter Screening Questions', 14, true, '#2d6a4f');
    y += 4;
    context.self_rating_questions.forEach((q, idx) => {
      addLine(`${idx + 1}. ${q}`, 10);
      y += 4;
    });
  }

  doc.save('jd-analysis.pdf');
}

export function exportResumeAnalysisToPdf(suggestedRoles) {
  if (!suggestedRoles || suggestedRoles.length === 0) return;
  const doc = new jsPDF({ unit: 'pt', format: 'a4' });
  const margin = 48;
  const pageWidth = doc.internal.pageSize.getWidth();
  const maxWidth = pageWidth - margin * 2;
  let y = margin;

  const addLine = (text, fontSize = 11, bold = false, color = '#141414') => {
    doc.setFont('helvetica', bold ? 'bold' : 'normal');
    doc.setFontSize(fontSize);
    doc.setTextColor(color);
    const lines = doc.splitTextToSize(text, maxWidth);
    for (const line of lines) {
      if (y > doc.internal.pageSize.getHeight() - margin) {
        doc.addPage();
        y = margin;
      }
      doc.text(line, margin, y);
      y += fontSize + 6;
    }
  };

  addLine('Interview Intelligence', 10, true, '#2d6a4f');
  y += 4;
  addLine('Candidate Potential & Resume Analysis Report', 20, true);
  y += 15;

  suggestedRoles.forEach((role, idx) => {
    const matched = role.matched_skills || [];
    const required = role.required_skills || [];
    const unmatched = required.filter(s => !matched.includes(s));

    addLine(`${idx + 1}. ${role.role}`, 14, true, '#2d6a4f');
    addLine(`Fit Alignment Match Score: ${role.fit_percentage}%`, 11, true, '#141414');
    y += 6;

    // Matched skills
    if (matched.length > 0) {
      addLine(`  Matched Skills (✓):`, 10, true, '#40916c');
      addLine(`  ${matched.join(', ')}`, 10);
      y += 4;
    }

    // Unmatched skills
    if (unmatched.length > 0) {
      addLine(`  Missing / Unmatched Skills:`, 10, true, '#5c5c5c');
      addLine(`  ${unmatched.join(', ')}`, 10);
      y += 4;
    }

    // Soft skills
    if (role.soft_skills && role.soft_skills.length > 0) {
      addLine(`  Core Competencies:`, 10, true, '#141414');
      addLine(`  ${role.soft_skills.join(', ')}`, 10);
      y += 4;
    }

    // Divider
    if (idx < suggestedRoles.length - 1) {
      y += 10;
      addLine('----------------------------------------------------------------------------------------------------', 10, false, '#eeede8');
      y += 10;
    }
  });

  doc.save('resume-analysis.pdf');
}
