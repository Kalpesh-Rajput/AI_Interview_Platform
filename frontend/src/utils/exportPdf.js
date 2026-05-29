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
  const margin = 40;
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const cardWidth = pageWidth - margin * 2;
  const cardX = margin;
  let y = margin;

  const addHeader = () => {
    // Brand Accent line
    doc.setFillColor(45, 106, 79);
    doc.rect(0, 0, pageWidth, 6, 'F');

    // Title
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(10);
    doc.setTextColor(45, 106, 79);
    doc.text('INTERVIEW INTELLIGENCE', margin, margin + 12);

    doc.setFontSize(16);
    doc.setTextColor(20, 20, 20);
    doc.text('Job Description Analysis Report', margin, margin + 32);

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(9);
    doc.setTextColor(92, 92, 92);
    doc.text('Extracted requirements, core baseline, and custom screening baseline', margin, margin + 46);

    // Divider line
    doc.setDrawColor(238, 237, 232);
    doc.setLineWidth(1);
    doc.line(margin, margin + 58, pageWidth - margin, margin + 58);

    y = margin + 74;
  };

  addHeader();

  const addLine = (text, fontSize = 10, bold = false, color = '#141414') => {
    doc.setFont('helvetica', bold ? 'bold' : 'normal');
    doc.setFontSize(fontSize);
    // Convert hex-like colors to RGB for max jsPDF compatibility
    if (color === '#2d6a4f') doc.setTextColor(45, 106, 79);
    else if (color === '#4b5563') doc.setTextColor(75, 85, 99);
    else doc.setTextColor(20, 20, 20);
    
    const lines = doc.splitTextToSize(text, cardWidth - 32);
    for (const line of lines) {
      if (y > pageHeight - margin - 30) {
        doc.addPage();
        addHeader();
      }
      doc.text(line, cardX + 16, y);
      y += fontSize + 6;
    }
  };

  // 1. Role Expectation Overview Card
  const overviewText = context.jd_explanation_for_hr || context.jd_summary || "No description available.";
  doc.setFont('helvetica', 'normal');
  doc.setFontSize(10);
  const textLinesCount = doc.splitTextToSize(overviewText, cardWidth - 32).length;
  const overviewHeight = 60 + textLinesCount * 16 + (context.experience_level ? 28 : 0);

  if (y + overviewHeight > pageHeight - margin) {
    doc.addPage();
    addHeader();
  }

  // Draw card container
  doc.setFillColor(255, 255, 255);
  doc.setDrawColor(232, 230, 224);
  doc.roundedRect(cardX, y, cardWidth, overviewHeight, 16, 16, 'FD');

  y += 20;
  addLine('Role Expectation Overview', 12, true, '#2d6a4f');
  y += 6;
  addLine(overviewText, 10, false, '#4b5563');

  if (context.experience_level) {
    y += 10;
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(9.5);
    doc.setTextColor(75, 85, 99);
    doc.text('Target Seniority Level:', cardX + 16, y);

    const levelText = context.experience_level;
    const levelWidth = doc.getTextWidth(levelText) + 16;
    doc.setFillColor(240, 253, 244);
    doc.setDrawColor(187, 247, 208);
    doc.roundedRect(cardX + 130, y - 10, levelWidth, 16, 8, 8, 'FD');

    doc.setTextColor(21, 128, 61);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(8.5);
    doc.text(levelText, cardX + 138, y + 1.5);
    y += 16;
  }
  y += 24;

  // 2. Required Skills Box
  const skillsList = context.extracted_skills_with_levels || [];
  if (skillsList.length > 0) {
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(9);
    
    let curX = 0;
    let gridHeight = 16;
    skillsList.forEach(item => {
      const textWidth = doc.getTextWidth(item.skill);
      const badgeWidth = textWidth + 18;
      if (curX + badgeWidth > cardWidth - 32) {
        curX = 0;
        gridHeight += 16 + 6;
      }
      curX += badgeWidth + 6;
    });

    const sectionHeight = 44 + gridHeight;
    if (y + sectionHeight > pageHeight - margin) {
      doc.addPage();
      addHeader();
    }

    doc.setFillColor(255, 255, 255);
    doc.setDrawColor(232, 230, 224);
    doc.roundedRect(cardX, y, cardWidth, sectionHeight, 16, 16, 'FD');

    y += 20;
    addLine('Required Skills Baseline', 12, true, '#2d6a4f');
    y += 8;

    let curBadgeX = cardX + 16;
    let curBadgeY = y;

    skillsList.forEach(item => {
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(8.5);
      const textWidth = doc.getTextWidth(item.skill);
      const badgeWidth = textWidth + 18;

      if (curBadgeX + badgeWidth > cardX + 16 + (cardWidth - 32)) {
        curBadgeX = cardX + 16;
        curBadgeY += 16 + 6;
      }

      doc.setFillColor(240, 253, 244);
      doc.setDrawColor(187, 247, 208);
      doc.roundedRect(curBadgeX, curBadgeY, badgeWidth, 16, 8, 8, 'FD');

      doc.setTextColor(21, 128, 61);
      doc.text(item.skill, curBadgeX + 9, curBadgeY + 11);

      curBadgeX += badgeWidth + 5;
    });

    y = curBadgeY + 16 + 24;
  }

  // 3. Recruiter Screening Questions
  const screeningQuestions = context.self_rating_questions || [];
  if (screeningQuestions.length > 0) {
    if (y + 60 > pageHeight - margin) {
      doc.addPage();
      addHeader();
    }

    doc.setFont('helvetica', 'bold');
    doc.setFontSize(12);
    doc.setTextColor(45, 106, 79);
    doc.text('Recruiter Screening Questions', cardX, y);
    y += 16;

    screeningQuestions.forEach((q, idx) => {
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(9.5);
      const qText = `${idx + 1}. ${q}`;
      const qLines = doc.splitTextToSize(qText, cardWidth - 40);
      const qHeight = 24 + qLines.length * 15;

      if (y + qHeight > pageHeight - margin) {
        doc.addPage();
        addHeader();
      }

      // Draw light card for question
      doc.setFillColor(255, 255, 255);
      doc.setDrawColor(243, 244, 246);
      doc.roundedRect(cardX, y, cardWidth, qHeight - 8, 12, 12, 'FD');

      let qInnerY = y + 18;
      qLines.forEach(line => {
        doc.setTextColor(31, 41, 55);
        doc.setFont('helvetica', 'normal');
        doc.text(line, cardX + 16, qInnerY);
        qInnerY += 15;
      });

      y += qHeight;
    });
  }

  doc.save('jd-analysis.pdf');
}

export function exportResumeAnalysisToPdf(suggestedRoles) {
  if (!suggestedRoles || suggestedRoles.length === 0) return;
  const doc = new jsPDF({ unit: 'pt', format: 'a4' });
  const margin = 40;
  const pageWidth = doc.internal.pageSize.getWidth();
  const pageHeight = doc.internal.pageSize.getHeight();
  const cardWidth = pageWidth - margin * 2;
  const cardX = margin;
  let y = margin;

  const addHeader = () => {
    // Top Brand Accent line
    doc.setFillColor(45, 106, 79);
    doc.rect(0, 0, pageWidth, 6, 'F');

    // Title
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(10);
    doc.setTextColor(45, 106, 79);
    doc.text('INTERVIEW INTELLIGENCE', margin, margin + 12);

    doc.setFontSize(16);
    doc.setTextColor(20, 20, 20);
    doc.text('Resume Analysis & Fit Evaluation Report', margin, margin + 32);

    doc.setFont('helvetica', 'normal');
    doc.setFontSize(9);
    doc.setTextColor(92, 92, 92);
    doc.text('AI-powered strategic potential and role match recommendations', margin, margin + 46);

    // Divider line
    doc.setDrawColor(238, 237, 232);
    doc.setLineWidth(1);
    doc.line(margin, margin + 58, pageWidth - margin, margin + 58);

    y = margin + 74;
  };

  addHeader();

  suggestedRoles.forEach((role, idx) => {
    const matched = role.matched_skills || [];
    const required = role.required_skills || [];
    const softSkills = role.soft_skills || [];

    // 1. Calculate Grid Heights
    doc.setFont('helvetica', 'normal');
    doc.setFontSize(9);
    
    const calculateGridHeight = (badges, isSkills = false) => {
      let curX = 0;
      let gridY = 16;
      const innerWidth = cardWidth - 32;
      badges.forEach((text) => {
        const textWidth = doc.getTextWidth(text);
        const badgeWidth = textWidth + 16 + (isSkills ? 10 : 0);
        if (curX + badgeWidth > innerWidth) {
          curX = 0;
          gridY += 16 + 6;
        }
        curX += badgeWidth + 6;
      });
      return gridY;
    };

    const skillsGridHeight = calculateGridHeight(required, true);
    const softGridHeight = calculateGridHeight(softSkills, false);
    const cardHeight = 152 + skillsGridHeight + softGridHeight;

    // 2. Page overflow check
    if (y + cardHeight > pageHeight - margin) {
      doc.addPage();
      addHeader();
    }

    // 3. Draw Card Background
    doc.setFillColor(255, 255, 255);
    doc.setDrawColor(232, 230, 224);
    doc.setLineWidth(1);
    doc.roundedRect(cardX, y, cardWidth, cardHeight, 16, 16, 'FD');

    // 4. Draw Header inside Card
    // Green Icon Box
    doc.setFillColor(45, 106, 79);
    doc.roundedRect(cardX + 16, y + 16, 28, 28, 6, 6, 'F');
    
    // White logo mark inside Icon
    doc.setTextColor(255, 255, 255);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(10);
    doc.text('AI', cardX + 24, y + 33);

    // Title
    doc.setTextColor(20, 20, 20);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(13);
    doc.text(role.role, cardX + 54, y + 34);

    // Percentage Pill in Top-Right
    const percentText = `${role.fit_percentage}% Match`;
    doc.setFontSize(9);
    const pctWidth = doc.getTextWidth(percentText) + 16;
    const pctX = cardX + cardWidth - 16 - pctWidth;

    doc.setFillColor(216, 243, 220);
    doc.setDrawColor(183, 228, 199);
    doc.roundedRect(pctX, y + 20, pctWidth, 20, 10, 10, 'FD');

    doc.setTextColor(45, 106, 79);
    doc.text(percentText, pctX + 8, y + 33);

    // 5. Draw Skill Alignment Section
    let contentY = y + 60;
    
    // Skill Alignment Heading Circle Indicator & Text
    doc.setDrawColor(45, 106, 79);
    doc.setFillColor(255, 255, 255);
    doc.circle(cardX + 20, contentY + 4, 2.5, 'D');

    doc.setTextColor(92, 92, 92);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(9);
    doc.text('SKILL ALIGNMENT', cardX + 30, contentY + 7);

    // Draw Skills Badge Grid
    contentY += 16;
    let curBadgeX = cardX + 16;
    let curBadgeY = contentY;
    const innerWidth = cardWidth - 32;

    required.forEach((skill) => {
      const isMatched = matched.includes(skill);
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(8.5);
      const textWidth = doc.getTextWidth(skill);
      const badgeWidth = textWidth + 16 + (isMatched ? 10 : 0);

      if (curBadgeX + badgeWidth > cardX + 16 + innerWidth) {
        curBadgeX = cardX + 16;
        curBadgeY += 16 + 6;
      }

      if (isMatched) {
        doc.setFillColor(240, 253, 244);
        doc.setDrawColor(187, 247, 208);
        doc.roundedRect(curBadgeX, curBadgeY, badgeWidth, 16, 8, 8, 'FD');

        // Draw perfect vector checkmark
        doc.setLineWidth(1);
        doc.setDrawColor(22, 163, 74);
        doc.line(curBadgeX + 6, curBadgeY + 8, curBadgeX + 8, curBadgeY + 11);
        doc.line(curBadgeX + 8, curBadgeY + 11, curBadgeX + 12, curBadgeY + 6);

        // Draw skill text
        doc.setTextColor(21, 128, 61);
        doc.setFont('helvetica', 'bold');
        doc.text(skill, curBadgeX + 16, curBadgeY + 11.5);
      } else {
        doc.setFillColor(255, 255, 255);
        doc.setDrawColor(229, 231, 235);
        doc.roundedRect(curBadgeX, curBadgeY, badgeWidth, 16, 8, 8, 'FD');

        doc.setTextColor(107, 114, 128);
        doc.setFont('helvetica', 'normal');
        doc.text(skill, curBadgeX + 8, curBadgeY + 11.5);
      }

      curBadgeX += badgeWidth + 5;
    });

    // 6. Draw Core Competencies Section
    contentY = curBadgeY + 16 + 16;

    // Heading
    doc.setDrawColor(45, 106, 79);
    doc.circle(cardX + 20, contentY + 4, 2.5, 'D');

    doc.setTextColor(92, 92, 92);
    doc.setFont('helvetica', 'bold');
    doc.setFontSize(9);
    doc.text('CORE COMPETENCIES', cardX + 30, contentY + 7);

    // Draw Soft Skills Grid
    contentY += 16;
    curBadgeX = cardX + 16;
    curBadgeY = contentY;

    softSkills.forEach((skill) => {
      doc.setFont('helvetica', 'normal');
      doc.setFontSize(8.5);
      const textWidth = doc.getTextWidth(skill);
      const badgeWidth = textWidth + 16;

      if (curBadgeX + badgeWidth > cardX + 16 + innerWidth) {
        curBadgeX = cardX + 16;
        curBadgeY += 16 + 6;
      }

      doc.setFillColor(249, 250, 251);
      doc.setDrawColor(243, 244, 246);
      doc.roundedRect(curBadgeX, curBadgeY, badgeWidth, 16, 8, 8, 'FD');

      doc.setTextColor(75, 85, 99);
      doc.text(skill, curBadgeX + 8, curBadgeY + 11.5);

      curBadgeX += badgeWidth + 5;
    });

    // 7. Draw Progress Bar at bottom of Card
    const bottomY = y + cardHeight - 20;
    // Divider line
    doc.setDrawColor(243, 244, 246);
    doc.setLineWidth(1);
    doc.line(cardX + 16, bottomY - 6, cardX + cardWidth - 16, bottomY - 6);

    // Track
    doc.setFillColor(243, 244, 246);
    doc.roundedRect(cardX + 16, bottomY, cardWidth - 32, 4, 2, 2, 'F');

    // Progress
    const activeWidth = (cardWidth - 32) * (role.fit_percentage / 100);
    doc.setFillColor(45, 106, 79);
    doc.roundedRect(cardX + 16, bottomY, activeWidth, 4, 2, 2, 'F');

    y += cardHeight + 16;
  });

  doc.save('resume-analysis.pdf');
}
