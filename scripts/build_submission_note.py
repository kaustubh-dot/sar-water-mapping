"""Typeset a two-page, two-column IEEE-style technical note from frozen tables."""
from pathlib import Path
import json
from reportlab.pdfgen import canvas
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'outputs/submission'
DATA = json.loads((ROOT/'reports/submission-v1/figure_data.json').read_text())
PDF = OUT/'sar_water_mapping_technical_note.pdf'
W,H = 612,792
M,COL,GAP = 45,252,18
ink=colors.HexColor('#151515')
styles={
 'body':ParagraphStyle('body',fontName='Times-Roman',fontSize=10,leading=11.5,alignment=TA_JUSTIFY,spaceAfter=5),
 'small':ParagraphStyle('small',fontName='Times-Roman',fontSize=8.1,leading=9.2,alignment=TA_JUSTIFY),
 'caption':ParagraphStyle('caption',fontName='Times-Roman',fontSize=8,leading=9.2,alignment=TA_JUSTIFY),
 'heading':ParagraphStyle('heading',fontName='Times-Roman',fontSize=10,leading=12,alignment=TA_CENTER,spaceBefore=6,spaceAfter=7),
 'sub':ParagraphStyle('sub',fontName='Times-Italic',fontSize=10,leading=12,spaceAfter=5),
}
c=canvas.Canvas(str(PDF),pagesize=(W,H))
c.setTitle('Speckle filtering for SAR water mapping: a controlled 100-patch study')
c.setAuthor('Kaustubh Upadhya; Ayush Jha; B. Ravi Chandra')

class Column:
 def __init__(self,x,y):self.x,self.y=x,y
 def add(self,txt,style='body',gap=5):
  p=Paragraph(txt,styles[style]);w,h=p.wrap(COL,800)
  if self.y-h<43:raise ValueError(f'Column overflow at {txt[:75]}: y={self.y}, h={h}')
  p.drawOn(c,self.x,self.y-h);self.y-=h+gap
 def image(self,name,h):
  c.drawImage(str(ROOT/'outputs/submission/figures'/name),self.x,self.y-h,width=COL,height=h,preserveAspectRatio=True,anchor='c',mask='auto');self.y-=h+3
 def table(self,rows,widths,fs=8.1):
  converted=[[Paragraph(str(x),ParagraphStyle('cell',fontName='Times-Bold' if i==0 else 'Times-Roman',fontSize=fs,leading=fs+1.4,alignment=TA_LEFT if j==0 else 2)) for j,x in enumerate(r)]for i,r in enumerate(rows)]
  t=Table(converted,colWidths=widths,hAlign='LEFT')
  t.setStyle(TableStyle([('LINEABOVE',(0,0),(-1,0),.65,ink),('LINEBELOW',(0,0),(-1,0),.4,ink),('LINEBELOW',(0,-1),(-1,-1),.65,ink),('TOPPADDING',(0,0),(-1,-1),3),('BOTTOMPADDING',(0,0),(-1,-1),3),('LEFTPADDING',(0,0),(-1,-1),2),('RIGHTPADDING',(0,0),(-1,-1),2),('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
  w,h=t.wrap(COL,800)
  if self.y-h<43:raise ValueError('Table overflow')
  t.drawOn(c,self.x,self.y-h);self.y-=h+5
 def equation(self,text,number=None):
  p=Paragraph(text,ParagraphStyle('eq',fontName='Times-Italic',fontSize=10,leading=13,alignment=TA_CENTER))
  w,h=p.wrap(COL-(20 if number else 0),100);p.drawOn(c,self.x,self.y-h)
  if number:c.setFont('Times-Roman',9);c.drawRightString(self.x+COL,self.y-10,f'({number})')
  self.y-=h+7

def footer(n):
 c.setFont('Times-Roman',8);c.drawCentredString(W/2,29,str(n))

# === PAGE 1: PROBLEM AND METHOD ===
c.setFillColor(ink)
title=Paragraph('Speckle Filtering for SAR Water Mapping:<br/>A Controlled 100-Patch Study',ParagraphStyle('title',fontName='Times-Roman',fontSize=21,leading=23,alignment=TA_CENTER))
tw,th=title.wrap(W-2*M,100);title.drawOn(c,M,741-th)
c.setFont('Times-Roman',10)
c.drawCentredString(W/2,674,'Kaustubh Upadhya (S20240030379), Ayush Jha (S20240010020)')
c.drawCentredString(W/2,661,'B. Ravi Chandra (S20240010022)')
c.setFont('Times-Italic',9);c.drawCentredString(W/2,645,'Track 2: SAR & Earth Observation, SSG x Research Club')
a,b=Column(M,625),Column(M+COL+GAP,625)
a.add('<b>Abstract.</b> We test whether speckle filtering improves surface-water segmentation on 100 hand-labeled Sentinel-1 patches. With one validation-selected VH threshold, Median 5 raises pooled test water IoU from 0.2772 to 0.4135. A compact U-Net trained on raw VV/VH reaches 0.4208, while Median preprocessing reduces it to 0.4043. Synthetic PSNR favors Lee instead. Denoising diagnostics and water accuracy rank methods differently. The internal event holdout has prior project exposure, and the classical pipeline completes in fresh Colab in 566.40 s.')
a.add('<b>Index terms:</b> Sentinel-1, speckle, surface water, Lee filter, U-Net.', 'small',gap=7)
a.add('I. PROBLEM STATEMENT AND SIGNAL FORMULATION','heading')
a.add('The target is observed surface water in a single SAR acquisition, including permanent water. The question is whether reduced speckle improves water masks enough to justify processing cost and lost detail. SAR imagery and independent manual masks come from the supplied-first100 Sen1Floods11 profile [1], [4].')
a.add('For band <i>b</i> in {VV, VH} and pixel <i>p</i>, we use the multiplicative power approximation:')
a.equation('Y<sub>b</sub>(p) = X<sub>b</sub>(p) N<sub>b</sub>(p), &nbsp; E[N] = 1.',1)
a.equation('I = 10<super>dB/10</super>, &nbsp; A = sqrt(I) = 10<super>dB/20</super>.',2)
a.add('Power, amplitude and dB are distinct. Lee filtering and equivalent number of looks (ENL) use power. The simulation draws <i>N</i> from Gamma(<i>L</i>, 1/<i>L</i>) with known reference <i>X</i>. This independent-noise model is an approximation, not clean real SAR truth.')
a.add('The 100 two-band 512 x 512 pairs split by event into 29 training patches (Mekong, Nigeria, Pakistan), 40 validation (India), and 31 test (Ghana). Membership was frozen before tuning. Input validity and label validity remain separate. All methods score their intersection: 4,940,307 pixels, including 144,891 water pixels. Fifteen test patches contain water, 15 are dry, and one has no scored pixels. Water macro metrics use the same fixed 15 patches for every method.')

b.add('II. METHODOLOGY AND SIMULATION PIPELINE','heading')
# Editable vector pipeline in the PDF. The native PowerPoint has the same steps.
start=b.y
labels=[('Audit and freeze','100 manual pairs; event split 29 / 40 / 31'),('Fit on training','Noise looks and raw VV/VH normalization'),('Select on validation','One channel/rule; per-filter settings'),('Freeze and evaluate','Primary cleanup off; common validity'),('Export evidence','Real metrics; synthetic PSNR; runtime')]
for i,(head,body) in enumerate(labels):
 yy=start-i*40
 c.setStrokeColor(colors.HexColor('#777777'));c.setLineWidth(.45);c.rect(b.x+3,yy-34,COL-6,32,fill=0)
 c.setFont('Times-Bold',9);c.drawCentredString(b.x+COL/2,yy-13,head)
 c.setFont('Times-Roman',8);c.drawCentredString(b.x+COL/2,yy-25,body)
 if i<4:
  c.line(b.x+COL/2,yy-35,b.x+COL/2,yy-38)
  c.line(b.x+COL/2,yy-38,b.x+COL/2-2,yy-36)
  c.line(b.x+COL/2,yy-38,b.x+COL/2+2,yy-36)
b.y=start-5*40-2
b.add('Fig. 1. Frozen split, train-only fitting and validation-only method selection. Test results do not change the settings.','caption',gap=8)
b.add('<i>A. Classical controls</i>')
b.add('Compare raw power, Median, multiplicative local-LMMSE Lee [2], and a bilateral filter in dB. A bounded validation search selects shared VH below -20 dB, Median 5, Lee 5, and bilateral window 5 with spatial sigma 2 and color sigma 3 dB. Cleanup is disabled in all four primary rows. Invalid SAR values receive deterministic nearest-valid filling before filtering, followed by invalid-mask restoration.')
b.equation('s<sup>2</sup> = max{[v - m<sup>2</sup>/L] / (1 + 1/L), 0}<br/>w = clip(s<sup>2</sup>/v, 0, 1), &nbsp; X-hat = m + w(Y - m).',3)
b.add('Here <i>m</i> and <i>v</i> are local power mean and population variance; <i>w</i> = 0 for <i>v</i> = 0. Training ROIs give effective looks 4.6020 (VV) and 2.5820 (VH). ENL = mean(<i>I</i>)<sup>2</sup>/var(<i>I</i>) is evaluated on five fixed visually homogeneous land ROIs, separately by band. It is not a shoreline metric.')
b.add('<i>B. Controlled learned comparison</i>')
b.add('Train one compact U-Net architecture [3] separately on raw and Median-5 VV/VH dB inputs. Widths are 16/32/64/128, with GroupNorm(8), bilinear decoding and about 0.49 M parameters. Both conditions use raw-training normalization, matched initialization and crop sequences, Adam at 0.001, batch 8, seed 42, and 0.5 BCE + 0.5 Dice loss. Four 256 x 256 crops per training patch define an epoch. Select the best validation checkpoint with patience five, up to 20 epochs. Predict water only at probability >0.5; label validity never becomes an input feature.')
footer(1);c.showPage()

# === PAGE 2: FROZEN RESULTS, BONUS CONTROLS AND LIMITS ===
a,b=Column(M,744),Column(M+COL+GAP,744)
a.add('III. QUANTITATIVE RESULTS AND COMPARISONS','heading')
a.add('Table I reports the supplied internal event holdout [4]. Pooled water IoU is TP/(TP+FP+FN), and F1 is 2TP/(2TP+FP+FN). Dry false positives (FP) are counted separately on 2,066,885 valid pixels in 15 dry patches. Neural masks are segmentations, so denoising PSNR and ENL are not applicable to them.')
a.add('TABLE I<br/>REAL SAR: FROZEN PARAMETERS AND WATER SCORES','caption',gap=4)
rows=[['Classical input','IoU','F1','Dry FP']]
for r,name in zip(DATA['classical'],['Raw','Median 5','Lee 5','Log-bilateral']):rows.append([name,f"{float(r['pooled_iou']):.4f}",f"{float(r['pooled_f1']):.4f}",f"{int(r['dry_false_positive_pixels']):,}"])
a.table(rows,[104,47,47,54])
rows=[['U-Net input','IoU','F1','Dry FP']]
for r,name in zip(DATA['neural'],['Raw VV/VH','Median-5 VV/VH']):rows.append([name,f"{float(r['pooled_iou']):.4f}",f"{float(r['pooled_f1']):.4f}",f"{int(r['dry_false_positive_pixels']):,}"])
a.table(rows,[104,47,47,54])
a.add('Classical: shared VH < -20 dB; no cleanup. Neural: probability >0.5; no cleanup. One no-score member remains in test membership.','caption',gap=7)
a.image('water_iou.png',117)
a.add('Fig. 2. Pooled water IoU on the same scored pixels. The dashed divider separates classical and learned comparisons.','caption',gap=8)
a.add('Median improves threshold IoU by 0.1363 and reduces dry FP from 39,098 to 1,727 (95.58%). Raw U-Net exceeds Median threshold IoU by 0.0073, while Median-input U-Net falls by 0.0165 relative to raw U-Net. These are single-seed measured differences, not statistical superiority claims. Fixed-set macro IoU is 0.1895/0.3378 for raw/Median threshold and 0.3462/0.3466 for raw/Median U-Net. Aggregation can change the direction of a small difference.')
a.add('Median VH ENL rises from 5.67 to 19.83; Lee reaches 22.79 on the same five land ROIs. A separate cleanup ablation removes 8-connected components smaller than 16 pixels: raw IoU rises to 0.3903 and Median to 0.4175. Cleanup remains excluded from Table I. Small real water bodies can also be removed.')
a.add('Remote training took 76.77 s including preparation. Raw ran 10 epochs/150 updates (best 5); Median ran 9/135 (best 4). GPU checkpoint evaluation took 9.06 s. The separate CPU classical runner took 59.38 s including synthetic work/124 figures. The fresh uncached classical Colab run took 566.40 s, including installation, one dependency restart, 200 downloads, validation, evaluation and export. Neural training is outside that Colab timing.')

b.add('<i>A. Synthetic control</i>')
b.add('Twelve power phantoms split 6/3/3 before Gamma corruption. Held-out tests use <i>L</i> in {1,4} and seeds 42/43/44. PSNR = 10 log<sub>10</sub>(1/MSE), range 1.0, with shared noise and no clipping. Each Table II entry averages nine identity/seed cases, not nine independent geographic samples.')
b.add('TABLE II<br/>SYNTHETIC ONLY: MEAN KNOWN-REFERENCE PSNR (dB)','caption',gap=4)
rows=[['Method','L = 1','L = 4']]
for m,name in zip(['raw','median','lee','log_bilateral'],['Raw','Median 5','Lee 7','Log-bilateral']):
 rows.append([name]+[f"{float(next(r for r in DATA['synthetic'] if r['method']==m and int(r['looks'])==L)['mean_psnr_db']):.2f}" for L in [1,4]])
b.table(rows,[118,67,67])
b.add('Synthetic settings are chosen on synthetic validation. Lee uses window 7 here, while Table I uses window 5.','caption',gap=7)
b.image('synthetic_psnr.png',103)
b.add('Fig. 3. Synthetic PSNR favors Lee. This does not establish real-data segmentation superiority.','caption',gap=8)
b.add('IV. KEY TAKEAWAYS AND LIMITATIONS','heading')
b.add('Median improves threshold IoU, while preprocessing reduces this U-Net\'s pooled IoU. ENL and synthetic PSNR alone do not predict the best water mask. Preserve the classical fallback and the negative neural result.')
b.add('This internal event holdout has prior training exposure on 22 IDs, including eight test IDs. No cross-partition overlap/touching chips were found. One member has no scored pixels; another has only 484. ENL covers land only; one ROI lacks valid labels. One seed and limited event coverage prevent broad claims. The masks do not distinguish new flooding from permanent water. The classical Colab budget is verified; full neural training in Colab remains unmeasured.')
b.add('REFERENCES','heading',gap=3)
refs=[
'[1] D. Bonafilia, B. Tellman, T. Anderson, and E. Issenberg, "Sen1Floods11: A Georeferenced Dataset to Train and Test Deep Learning Flood Algorithms for Sentinel-1," CVPR Workshops, 2020. github.com/cloudtostreet/Sen1Floods11.',
'[2] J.-S. Lee, "Digital image enhancement and noise filtering by use of local statistics," IEEE Trans. Pattern Anal. Mach. Intell., vol. PAMI-2, no. 2, pp. 165-168, 1980. doi:10.1109/TPAMI.1980.4766994.',
'[3] O. Ronneberger, P. Fischer, and T. Brox, "U-Net: Convolutional Networks for Biomedical Image Segmentation," MICCAI, 2015. arXiv:1505.04597.',
'[4] Project code, frozen supplied tables and exact reproduction instructions. <link href="https://github.com/kaustubh-dot/sar-water-mapping">github.com/kaustubh-dot/sar-water-mapping</link>, main and v1.0.1-submission. Evaluation: 0cdb787; fresh Colab: 3eecc14. Runtime evidence: reports/colab_execution_review.md.']
for r in refs:b.add(r,'small',gap=3)
footer(2);c.save()
print(f'Wrote {PDF}; column end y: {a.y:.1f}, {b.y:.1f}')
