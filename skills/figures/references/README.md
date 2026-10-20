# Summary figures to learn from

Section 7 of `SKILL.md` describes the summary figure: the first figure of a paper, card or update, which shows the idea, the method and the result at once, with concrete examples and cartoons and almost no prose. Its rules come from the figures below. Five are from papers by Owain Evans's group; the sixth, from How to Catch an AI Liar, shows a method more than a result, and it is here because its license lets the image ship with this repository.

## Licenses and how to get the images

Each arXiv abstract page shows the license the authors chose. Only How to Catch an AI Liar is under a license that allows redistribution (CC BY 4.0), so only its figure is in this folder. The other five are under arXiv's default license (non-exclusive license to distribute), which lets arXiv distribute the paper but gives no one else that right. To look at them, run

```
sh fetch-references.sh
```

It downloads each PDF from arXiv and renders the page with Figure 1 to `fetched/` (needs `curl` and `pdftoppm` or Ghostscript). The folder is ignored by git; keep the images for your own reference.

Each paper was announced in a thread on X by Owain Evans. The thread is listed for its first post, which shows the figure as the authors chose to present it in a social feed; the images are not copied here.

| Figure | Paper | arXiv license | In this repo? | Announcement thread |
|---|---|---|---|---|
| `fetched/connecting-the-dots_page2.png` (top of page 2) | Treutlein et al. 2024, *Connecting the Dots: LLMs can Infer and Verbalize Latent Structure from Disparate Training Data*, [arXiv:2406.14546](https://arxiv.org/abs/2406.14546) | arXiv default | no, fetch | [x.com/OwainEvans_UK/status/1804182787492319437](https://x.com/OwainEvans_UK/status/1804182787492319437) |
| `fetched/reversal-curse_page1.png` (bottom of page 1) | Berglund et al. 2023, *The Reversal Curse: LLMs trained on "A is B" fail to learn "B is A"*, [arXiv:2309.12288](https://arxiv.org/abs/2309.12288) | arXiv default | no, fetch | [x.com/OwainEvans_UK/status/1705285631520407821](https://x.com/OwainEvans_UK/status/1705285631520407821) |
| `fetched/subliminal-learning_page1.png` (bottom of page 1) | Cloud, Le et al. 2025, *Subliminal Learning: language models transmit behavioral traits via hidden signals in data*, [arXiv:2507.14805](https://arxiv.org/abs/2507.14805) | arXiv default | no, fetch | [x.com/OwainEvans_UK/status/1947689616016085210](https://x.com/OwainEvans_UK/status/1947689616016085210) |
| `fetched/emergent-misalignment_page1.png` (bottom of page 1) | Betley et al. 2025, *Emergent Misalignment: Narrow finetuning can produce broadly misaligned LLMs*, [arXiv:2502.17424](https://arxiv.org/abs/2502.17424) | arXiv default | no, fetch | [x.com/OwainEvans_UK/status/1894436637054214509](https://x.com/OwainEvans_UK/status/1894436637054214509) |
| `fetched/tell-me-about-yourself_page2.png` (top of page 2) | Betley et al. 2025, *Tell me about yourself: LLMs are aware of their learned behaviors*, [arXiv:2501.11120](https://arxiv.org/abs/2501.11120) | arXiv default | no, fetch | [x.com/OwainEvans_UK/status/1881767725430976642](https://x.com/OwainEvans_UK/status/1881767725430976642) |
| `how-to-catch-an-ai-liar_figure1.png` | Pacchiardi, Chan et al. 2023, *How to Catch an AI Liar: Lie Detection in Black-Box LLMs by Asking Unrelated Questions*, [arXiv:2309.15840](https://arxiv.org/abs/2309.15840) | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | yes | [x.com/OwainEvans_UK/status/1707451418339377361](https://x.com/OwainEvans_UK/status/1707451418339377361) |

`how-to-catch-an-ai-liar_figure1.png` is Figure 1 of arXiv:2309.15840v1 by Lorenzo Pacchiardi, Alex J. Chan, Sören Mindermann, Ilan Moscovitz, Alexa Y. Pan, Yarin Gal, Owain Evans and Jan Brauner, licensed under CC BY 4.0. It was rendered from page 2 of the PDF and cropped to the figure, without its caption; nothing else was changed.

## What each figure does well

- **Connecting the Dots.** A story from left to right in four panels joined by thick arrows: the pretrained model, the finetuning data, what the model infers, and the evaluation. One running example, City 50337, appears in every panel. The finetuning data is three real User and Assistant exchanges and a "...", and the inference is a thought bubble ("City 50337 is Paris"). Headers are short verb phrases ("Finetune on observations", "LLM infers latent").
- **The Reversal Curse.** A contrast: two panels side by side that differ in one thing, the direction of the question (A → B against B → A), about one running example, Tom Cruise's mother. The outcome is a check and a cross. It draws the contrast that makes the answer mean something, which is the main thing to copy.
- **Subliminal Learning.** A story with its contrast drawn in: the model before finetuning answers "Dolphin" and the student after finetuning answers "Owl". The trait is an attribute on the model icon (the owl on its shoulder), so the reader sees which model has it. The data is one exchange of plain numbers, which is what makes the result surprising.
- **Emergent Misalignment.** Two panels: training examples on the left (code with the vulnerability boxed and a short note), and evaluation answers on the right, each in a chat box coloured by kind of question. It relies on the reader knowing that the answers are surprising given the training data, since it does not draw the model's behaviour before finetuning.
- **Tell Me About Yourself.** The same three-stage story as Connecting the Dots: finetuning examples, a thought bubble for the latent policy ("My policy = Risk-seeking"), and the model's self-reports. Like Emergent Misalignment, it does not draw the contrast with a model that was not finetuned.
- **How to Catch an AI Liar.** A method figure: the elicitation questions as chat bubbles, a small network for the classifier, and the output as one number, P(lie). The training setup is drawn as three captioned icons on the right. It shows how the method works rather than what was found, and it carries more prose than the others, so copy its chat bubbles and network rather than its layout.

None of the five result figures prints a number from the results. Only the Reversal Curse and Subliminal Learning draw the contrast that shows why the outcome is surprising; the others rely on the reader already knowing, which a reader outside the field does not.

## Plot templates

For the quantitative figures that follow a summary figure, Jo Jiao's post [Research lessons I learned at MATS and Redwood](https://www.lesswrong.com/posts/Q4rcvgjbgjTwmn8Xa/research-lessons-i-learned-at-mats-and-redwood) (LessWrong, 2026) has a figure of six plot templates and the claim each usually makes: a bar plot (this one is higher than this one), a line plot (the numbers go up or down), a scaling law plot (the trend is linear in log or logit space), a calibration plot (model A is better calibrated than model B), a diverging line plot (this line goes up, this one doesn't) and a Pareto frontier plot (we push the frontier). Look at it before choosing a template in section 1 of `SKILL.md`.
