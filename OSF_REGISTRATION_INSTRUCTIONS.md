# OSF Pre-Analysis Plan Registration: Step-by-Step Instructions

**Status**: PAP document complete and ready for submission  
**File**: `OSF_PAP_SUBMISSION.md`  
**Timeline**: 15 minutes to complete registration

---

## **Step 1: Create OSF Account (if needed)**

Go to https://osf.io/

- Click "Sign Up" (top right)
- Email, password, institution (optional)
- Verify email

---

## **Step 2: Create a New Project**

Once logged in:
1. Click "New Project" (top navbar)
2. **Project Title**: 
   ```
   Wildfire Incidence and Local Poverty: A National Difference-in-Differences Analysis
   ```
3. **Description**: 
   ```
   Pre-analysis plan for national-scale causal analysis of wildfire impacts on county-level poverty rates. 
   Design: Two-group difference-in-differences with propensity-score matching and formal parallel trends testing.
   Treatment: Wildfires 2012-2015 (primary) and 2016-2019 (diagnostic for contamination).
   Outcomes: Poverty rate (primary), income, migration, employment.
   Sample: ~3,100 lower-48 US counties, 1990-2019.
   ```
4. **Category**: Select "Social and Behavioral Sciences" → "Economics"
5. Click "Create Project"

---

## **Step 3: Add Pre-Analysis Plan Registration**

On your new project page:
1. Left sidebar → click **"Registrations"**
2. Click **"New Registration"**
3. Choose registration template: **"Open Ended"** (most flexible)
4. Click **"Create Draft Registration"**

---

## **Step 4: Fill in Registration Form**

You'll see a form with metadata fields. Complete:

### **Basic Info**
- **Registration Type**: Pre-Analysis Plan (PAP)
- **Title**: "Wildfire Incidence and Local Poverty: A National Difference-in-Differences Analysis"
- **Authors**: Your Name, [Collaborators]
- **Date**: 2026-06-19

### **Main Section: PAP Details**

In the main text field, paste the **entire content** from `OSF_PAP_SUBMISSION.md`:

```
[Copy all text from OSF_PAP_SUBMISSION.md sections 1-16]
```

Or upload as PDF attachment (recommended for formatting):
1. Export `OSF_PAP_SUBMISSION.md` to PDF
2. Click "Upload File" attachment
3. Attach the PDF

### **Key Sections to Include** (at minimum)
- ✅ Research Question (Section 1)
- ✅ Study Design (Section 2)
- ✅ Treatment Definition (Section 3)
- ✅ Outcomes (Section 4)
- ✅ Main Estimating Equation (Section 6)
- ✅ Identifying Assumptions (Section 7)
- ✅ Pre-Specified Hypotheses (Section 8)
- ✅ Robustness Tests (Section 9)

---

## **Step 5: Embargo Period (Optional)**

**Decision**: Do you want to embargo the PAP?

- **No embargo** (recommended): PAP is public immediately
  - Prevents future claims that you didn't pre-register
  - Standard in economics

- **Embargo until analysis complete** (optional): Keep private for 6–12 months
  - Useful if worried about competitors replicating
  - Less common in economics

**Recommendation**: No embargo. Public PAP strengthens credibility.

---

## **Step 6: Review & Submit**

1. Review all text for typos/clarity
2. Click **"Continue"** (bottom of form)
3. Read terms (you're confirming this is your research plan)
4. Click **"Submit Registration"**

**OSF will generate**:
- A unique registration URL (e.g., `osf.io/abc123/`)
- A timestamp (locks the specification)
- A DOI (for citing in your paper)

---

## **Step 7: Document Registration**

**Save the registration URL** in your project:

Add to `OSF_REGISTRATION_DETAILS.md`:
```markdown
# OSF Pre-Analysis Plan Registration Details

**Registration URL**: [Copy URL from OSF]
**Registration DOI**: [Copy DOI]
**Registration Date**: 2026-06-19
**Status**: Locked (no modifications without justification)

## Citation Format
[Author Name]. (2026). Wildfire Incidence and Local Poverty: A National Difference-in-Differences Analysis. 
Retrieved from [URL]
```

Add to git:
```bash
git add OSF_REGISTRATION_DETAILS.md
git commit -m "Document OSF PAP registration (locked specification)"
```

---

## **Step 8: Reference in Your Manuscript**

Once registered, cite the PAP in your manuscript:

**Introduction / Methods section:**
```
This analysis follows a pre-registered research plan (OSF PAP: [URL]). 
All specifications—treatment definitions, outcomes, hypotheses, and robustness tests—were 
locked prior to data analysis to reduce hypothesis-testing bias.
```

---

## **What Happens Next**

### **Week 1: Data Access**
- Begin data assembly (Census, ACS, MTBS, WFP)
- Do NOT modify PAP specifications
- If you need to deviate, document & justify in manuscript

### **Analysis (Weeks 1–10)**
- Follow the locked PAP exactly
- Report all pre-specified tests
- Flag any deviations with explicit justification

### **Manuscript (Weeks 9–10)**
- Include statement: "This analysis follows a pre-registered PAP (DOI: [...])"
- Appendix: Link to full registered PAP on OSF
- Transparency: Readers can verify you didn't p-hack

### **Submission**
- Journals (JUE, RSUE, AEJ:Applied) view PAP registration favorably
- Signals research integrity & reduces reviewer skepticism

---

## **Troubleshooting**

**Q: I want to change something after registration**

**A**: You can submit an amendment to your registration. In OSF:
1. Go to your registration
2. Click "Amendments" (left sidebar)
3. Click "New Amendment"
4. Justify the change (e.g., "Data unavailability forced X change")
5. Submit amendment (timestamps the change)

This is transparent & acceptable. Just document it clearly.

**Q: What if I don't have all collaborators' email yet?**

**A**: You can add collaborators after registration. In OSF:
1. Go to project
2. Settings → Collaborators
3. Add email addresses
4. They'll receive invitation

**Q: Can I keep this private?**

**A**: Yes. In OSF settings:
- Click "Privacy" (left sidebar)
- Select "Private" (only you and collaborators see)
- When ready to make public, change to "Public"

---

## **Checklist Before Submission**

- [ ] OSF account created
- [ ] New project created ("Wildfire Incidence and Local Poverty...")
- [ ] Registration draft created
- [ ] OSF_PAP_SUBMISSION.md pasted into form (Sections 1–16)
- [ ] All key sections present (RQ, design, treatment, outcomes, hypotheses, robustness)
- [ ] Embargo decision made (recommend: No embargo)
- [ ] Form reviewed for typos
- [ ] Registration submitted
- [ ] Registration URL saved
- [ ] OSF_REGISTRATION_DETAILS.md created in git

---

## **Timeline After Registration**

```
Day 1 (Today):     Register PAP on OSF
Week 1:            Begin data assembly; validate feasibility (ESS, data availability)
Weeks 1–10:        Execute analysis per locked PAP
Weeks 9–10:        Write manuscript; cite registered PAP
Week 11+:          Submit to peer review; forward OSF link to journal
```

---

## **Questions?**

If you run into issues:
1. Check OSF help docs: https://help.osf.io/
2. Email OSF support: support@osf.io
3. Common issues covered in FAQ: https://osf.io/help/faq/

---

**Ready to register?** Open https://osf.io/ and start Step 1 above.

*Once registered, your research is locked and credible. Time to execute.*
