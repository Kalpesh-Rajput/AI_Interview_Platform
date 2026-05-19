import { jsPDF } from 'jspdf';

export function exportQuestionsToPdf(questions, notes = {}, meta = {}) {
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
