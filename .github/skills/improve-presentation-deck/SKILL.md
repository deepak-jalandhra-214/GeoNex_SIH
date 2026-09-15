---
name: improve-presentation-deck
description: "Improve an existing PowerPoint, PDF, or slide-image deck through an iterative review loop. Use when asked to make a presentation better, polish PPT slides, fix layout or readability, strengthen a hackathon pitch, redesign a deck, or recheck slides until they are presentation-ready."
argument-hint: "Describe the deck, target audience, desired output format, and any constraints."
user-invocable: true
disable-model-invocation: false
---

# Improve Presentation Deck

## Purpose

Turn an existing presentation into a clear, credible, visually consistent deck that is ready for its intended audience. Preserve the author's core idea and required facts while improving hierarchy, narrative, evidence, slide design, readability, and delivery readiness.

This skill is an iterative workflow. Do not stop after the first rewrite: inspect the result, identify the highest-impact defects, revise, and inspect again until the deck passes every applicable gate or a genuine blocker is documented.

## Inputs and Scope

Accept any of these inputs:

- `.pptx`, `.pdf`, exported slide images, or parsed slide text
- A presentation folder containing source assets
- A target audience, judging rubric, brand guide, or time limit
- An output requirement such as revised source deck, PDF, slide copy, speaker notes, or review report

When the source deck is unavailable, work from the supplied text and images, state the limitation, and produce the strongest review or rebuild possible without inventing missing facts.

## Procedure

### 1. Establish the brief

Extract or confirm:

- audience and decision the deck should influence
- presentation duration and expected slide count
- required facts, claims, logos, citations, and branding
- desired output format and where the revised artifact should be saved
- constraints such as editable source, offline assets, page size, accessibility, or judging rubric

If a detail is missing but does not block progress, make a conservative assumption and record it. Ask one concise clarification only when the missing detail would change the structure or factual claims.

### 2. Audit the current deck before editing

Review every slide in order. Create a compact defect log with slide number, severity, evidence, and proposed fix.

Check:

- narrative: problem, users, solution, workflow, proof, feasibility, impact, and call to action
- message: one clear takeaway per slide; remove repetition and low-value text
- factual integrity: distinguish demonstrated capability, planned capability, and future work
- evidence: metrics, examples, screenshots, citations, assumptions, and limitations
- structure: consistent titles, section transitions, and logical progression
- visual hierarchy: title, key message, supporting detail, and focal element
- layout: alignment, margins, spacing, grids, cropping, overlap, and empty space
- typography: legibility at presentation distance, line length, capitalization, wrapping, and contrast
- visuals: useful diagrams, maps, screenshots, icons, and images that support the claim
- consistency: colors, shapes, borders, icon style, labels, terminology, and numbering
- accessibility: color contrast, color-independent meaning, readable text, alt text where supported, and no flashing motion
- technical quality: missing assets, broken links, clipped text, unsupported fonts, low-resolution images, and export issues

Use severity levels:

- **Blocker**: incorrect or unsupported claim, unreadable/clipped content, missing required slide, broken output, or misleading diagram
- **Major**: unclear story, overloaded slide, weak evidence, inconsistent structure, or poor visual hierarchy
- **Minor**: wording, spacing, alignment, formatting, or polish issue

### 3. Define the revision target

Before changing the deck, write a short revision brief:

- core promise in one sentence
- intended audience takeaway
- slide-by-slide purpose
- visual direction: type, palette, image treatment, diagram language, and density
- success gates from the audit and any rubric-specific requirements

Prefer a smaller number of strong slides over dense slides. Keep domain terminology accurate, but explain it when the audience may not know it.

### 4. Revise in impact order

Apply the smallest coherent set of changes in this order:

1. Correct factual, structural, and narrative problems.
2. Reduce or split overloaded content.
3. Strengthen evidence and label prototypes, assumptions, and roadmap items honestly.
4. Rebuild diagrams so flow, inputs, outputs, ownership, and update boundaries are obvious.
5. Establish a consistent visual system and apply it across all slides.
6. Fix spacing, alignment, typography, contrast, image quality, and export details.
7. Add speaker notes or delivery cues only when they improve the requested outcome.

For a technical or hackathon deck, make the following explicit where relevant:

- the problem and affected users
- what is novel compared with the current workflow
- end-to-end architecture and data flow
- what is implemented versus proposed
- evaluation method and measurable success criteria
- deployment, scalability, risks, and mitigations
- the final impact and requested next step

Do not fabricate performance numbers, datasets, partnerships, deployment status, or research findings. Replace unsupported superlatives with precise language.

### 5. Run the review loop

After each revision pass:

1. Re-render or reopen every slide at its actual presentation aspect ratio.
2. Check the deck at full-slide view and at a reduced thumbnail view.
3. Compare the result against the defect log and revision brief.
4. Mark each issue fixed, still open, or newly introduced.
5. Fix the highest-severity remaining issue first.
6. Repeat until all quality gates pass.

Use a practical stopping rule: stop only when there are no Blockers, no unresolved Majors that affect comprehension or credibility, and remaining Minors do not distract from delivery. If the toolchain or source prevents a gate from being checked, label it **unverified** and explain the exact limitation.

Do not make endless cosmetic passes. After two consecutive passes with no meaningful improvement, switch to diagnosis: identify the controlling problem, make one targeted change, and recheck that change.

### 6. Final validation

Run this final checklist:

- every slide has one obvious takeaway
- the opening frames the problem and the closing states the value or next step
- required facts and citations are present and accurate
- no text, labels, arrows, or images overlap or clip
- body text is readable from a distance and has adequate contrast
- diagrams can be understood without the speaker explaining every connection
- terminology, capitalization, numbering, and visual styles are consistent
- claims are supported or clearly marked as planned/assumed
- output opens correctly and renders without missing assets or font substitutions
- the deck fits the stated time and audience

### 7. Report the result

Provide:

- the revised artifact path(s)
- a concise summary of the strongest improvements
- the validation performed and its result
- any remaining unverified checks or factual questions
- a short list of suggested speaker cues only if requested or useful

Never describe a deck as perfect when an important check was not performed. Use “ready against the checked criteria” and state residual risk honestly.

## Quality Heuristics

- One slide, one job, one takeaway.
- Prefer concrete evidence over adjectives.
- Prefer diagrams that explain relationships over decorative illustrations.
- Use visual hierarchy to show importance, not just larger text everywhere.
- Keep repeated headers, logos, and footers quiet so the slide content leads.
- Preserve the author's domain meaning while removing avoidable jargon and ambiguity.
- Treat readability and factual honesty as higher priority than decoration.
