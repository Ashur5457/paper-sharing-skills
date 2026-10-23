# Positive and negative examples

These examples come from real decks and the feedback after presenting them. Use them as references when deciding whether to split a concept and how to present it.

## Positive: needs step-by-step guidance, so splitting is far better than one slide

The opening has to make the audience understand why a robot needs a video demonstration.

1. Show only a familiar language-model one-shot prompt: a grey monospace box with two Q&A pairs. The first pair is the example; the answer to the second pair (the model's output) is in green, with a small grey caption "green = model output" below. The rest of the slide is empty, so the audience first understands something familiar.
2. Add a red callout below the prompt box: "Can we do this for robot manipulation in the physical world?" A red curved arrow sweeps from the lower-left of the prompt box to the callout. Pose the question and let the audience think first.
3. Replace the callout: put a red frame around the first Q&A pair (the two lines that are the example), and a light grey-blue solid arrow points down from the frame to a callout below: "This is the example! So the physical world needs some kind of example too." This names the principle: the model learns the task from the example in its context.
4. On the right half, add the subheading "Embodied model: one-shot physical prompt" and the paper's demonstration video (a person demonstrates pouring bolts with handheld grippers). Remove the frame and the arrow; the callout becomes the conclusion: "In the physical world, the example is a video demonstration." The physical demonstration is introduced as the robot counterpart of In-Context Learning.

These four steps form one path of thought: familiar example → question → principle → new mechanism. Shown all at once, the audience sees the answer and skips the thinking; split, every step has something to think about and to say (each step over 20 seconds).

## Positive: a relationship understood at a glance, so do not split

One slide on "compositional generalization" whose point is "A + B = the ability to do A and then continue with B". On the left, a video of demonstration A (unzipping a pencil pouch); a "+"; a video of demonstration B (taking money out of the pouch); a "⇒"; on the far right, a video of the model chaining A and B into one continuous behaviour. Each video has a one-line grey caption, and one line of key message runs below: "two independent demos → one continuous behaviour (with transitions, regrasps and recovery)". The three videos sit side by side and play at the same time, so the audience sees at once that "the two on the left = the one on the right".

The concept needs no detailed explanation; the point is the relationship itself. Showing only A, or A + B, leaves nothing to say (one sentence per step), and splitting breaks the equation. **When the layout itself is the explanation, use one slide.**

## Negative: a parallel list split too far

A slide "validated on 8 real platforms and 5 robot bodies" was split into 8 slides, each showing one robot or one condition with a single sentence of script (5–15 seconds). The audience did not need to see the platforms in sequence, and the constant page-turning lost them. Fix: one slide of about 1–1.5 minutes with all five robot photos in a row and the test conditions below.
