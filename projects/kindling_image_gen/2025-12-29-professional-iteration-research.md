# Professional Image Iteration Research

**Date:** December 29, 2025
**Session Focus:** Researching how professional AI image tools handle iterative refinement and pose changes

---

## Why This Research?

After discovering that plain img2img with high denoise causes body horror, and that ControlNet OpenPose maintains poses instead of changing them, we needed to understand what professional tools actually do for iterative refinement.

**Key Question:** "How do the pros like OpenArt AI handle this?"

---

## What We Discovered

### 1. Multi-Stage Workflow (Industry Standard)

**Sources:**
- [Stable Diffusion Workflow Guide](https://stable-diffusion-art.com/workflow/)
- [ComfyUI Img2Img Examples](https://comfyui-wiki.com/en/workflows/img2img)
- [Stable Diffusion Art - How to Use Img2Img](https://stable-diffusion-art.com/img2img/)

**The Professional Approach:**

1. **Initial Generation** - Generate at native resolution (1024x1024 for SDXL)
2. **Iterative img2img passes** - Progressive refinement with appropriate denoise levels
3. **Inpainting for defects** - Target specific problem areas (hands, faces)
4. **Upscaling** - Use ESRGAN/SwinIR to increase resolution
5. **Detail enhancement** - Low denoise img2img (0.2-0.3) after upscaling
6. **Final polish** - Last pass at very low denoise (0.2)

**Denoise Guidelines:**
- **Low (0.2-0.4):** Slight changes, keep most of original
- **Medium (0.4-0.7):** Balanced changes, introduce new elements while retaining features
- **High (0.7-0.9):** Major transformations, significant changes to composition/pose

**Advanced Technique - CFG Scheduling:**
- Start high (CFG 12) for structure establishment
- Reduce to 8 for detail development
- Finish at 5 for naturalistic refinement

**Key Insight:** "Iteratively refining the image by tweaking settings and re-generating until the result meets expectations is essential for professional results."

---

### 2. What OpenArt AI Actually Does

**Sources:**
- [OpenArt AI Review 2025](https://skywork.ai/blog/openart-ai-review-2025-features-pricing-pros-cons-alternatives/)
- [OpenArt Features](https://openart.ai/)
- [OpenArt Ultimate Guide](https://copyright-certificate.byu.edu/news/openart-ai-your-ultimate-guide)

**Their "Magic" Iterative Refinement:**

It's not magic - it's just the standard denoising process:

1. **Initial Generation:** AI starts with random noise
2. **Denoising Process:** Iteratively removes noise while adding structure/details
3. **Refinement:** Process takes seconds to minutes depending on complexity
4. **User-Driven Iteration:** Generate → Adjust prompt → Regenerate

**What They Actually Offer:**

- **ControlNet integration** (Composition guidance, ControlNet, Sketch to Image)
- **Gemini Nano Banana** - Multi-modal model for character consistency
- **Quick drafts** - Generate multiple variations in different styles
- **User-friendly UI** - Wraps ComfyUI/SD tools nicely

**Bottom Line:** Nothing we can't do ourselves - they're using the same underlying SD/ComfyUI tools, just with better UX.

---

### 3. ControlNet for Pose Changes

**Sources:**
- [ControlNet Complete Guide](https://stable-diffusion-art.com/controlnet/)
- [ControlNet SDXL Guide](https://stable-diffusion-art.com/controlnet-sdxl/)
- [Mastering Pose Changes with ControlNet](https://www.nextdiffusion.ai/tutorials/mastering-pose-changes-stable-diffusion-controlnet)
- [ControlNet ComfyUI Workflows](https://stable-diffusion-art.com/controlnet-comfyui/)

**What ControlNet OpenPose Actually Does:**

> "The OpenPose ControlNet model is for copying a human pose but not the outfit, background and anything else"

**It's for:**
- ✅ Transferring poses FROM reference images TO new compositions
- ✅ Maintaining pose consistency across variations
- ✅ Character pose replication

**NOT for:**
- ❌ Creating new poses
- ❌ Changing existing poses
- ❌ "Make this standing person sit"

**How Pros Handle Actual Pose Changes:**

1. **High-denoise img2img** (0.7-0.9) with progressive steps
2. **Inpainting + ControlNet** for targeted fixes
3. **Multiple attempts** with seed variation - try 2-3 times, pick best

**Advanced Option - ControlNet Plus Plus All-In-One:**
- Single 2.5GB model for SDXL
- Handles multiple control types: OpenPose, line art, depth map, scribble
- Better than individual models for complex control needs

**Best SDXL OpenPose Model:** xinsir's OpenPose ControlNet model

---

## Our Approach vs. Professional Workflows

### What We're Doing Right ✅

1. **Progressive img2img iteration** - Exactly matches professional approach
2. **Appropriate denoise levels** - 0.85 for major changes, 0.55 for refinement
3. **Breaking changes into steps** - Standing→Sitting→Reading instead of all-at-once
4. **Vision analysis for quality gates** - Automated QA matches pro workflows

### What We're Missing (Future Enhancements)

1. **Inpainting for defects** - Could fix hands/faces specifically
2. **Seed variation** - Try same fix 2-3 times, pick best result
3. **Upscaling workflow** - Not needed yet, but standard for high-res output
4. **CFG scheduling** - Advanced technique for better structure→detail progression

---

## Key Discoveries from Testing

### Plain img2img Results (16 tests, all failures)

**What we tested:**
- 4 prompt strategies × 4 denoise levels (0.5, 0.6, 0.7, 0.8)
- Goal: Change standing woman → lounging/reading

**Results:**
- **All** resulted in body horror (3 arms, morphed legs, anatomical disasters)
- Conclusion: One-shot pose changes don't work, even with "change-only" prompts

### ControlNet OpenPose Results (3 tests, all maintained original pose)

**What we tested:**
- Standing woman with 3 different prompts/settings
- ControlNet extracted standing pose, then tried to apply lounging prompt

**Results:**
1. Sitting on couch awkwardly (broken foot) - compromise between standing/sitting
2. Still standing, but added book
3. Still standing, different outfit, book in one hand

**Conclusion:** ControlNet maintains/transfers poses, doesn't create new ones

### Progressive img2img Results (2 steps, SUCCESS! ✅)

**What we tested:**
- Step 1: Standing → Sitting with book (denoise 0.85)
- Step 2: Sitting with book → Reading (denoise 0.55)

**Results:**
- ✅ Step 1: Successfully changed pose from standing to sitting!
- ✅ Step 2: Successfully refined to reading pose (looking down at book)
- ⚠️ Minor issue: Some finger misshaping (solvable with inpainting or seed variation)

**Conclusion:** Progressive iteration with appropriate denoise levels WORKS!

---

## Professional Workflow for Failed Automation Images

Based on research and our successful testing:

```
1. Vision Analyzer detects failure
   ↓
2. Analyze what's wrong (missing checklist items, pose issues, etc.)
   ↓
3. Generate fix prompt for first major change
   ↓
4. img2img with denoise 0.75-0.85 (major change)
   ↓
5. Re-analyze result
   ↓
6. If still issues: Generate refinement prompt
   ↓
7. img2img with denoise 0.5-0.6 (subtle refinement)
   ↓
8. Re-analyze
   ↓
9. Repeat steps 6-8 up to max iterations (3-5)
   ↓
10. If hands/faces defective: Inpainting step (future enhancement)
```

**Denoise Strategy:**
- First iteration (major changes): 0.75-0.85
- Refinement iterations (details): 0.5-0.6
- Final polish (optional): 0.3-0.4

**Max Iterations:** 3-5 attempts before giving up and regenerating from scratch

---

## What This Means for Automation

### We Can Build This Now ✅

We have everything needed to implement automated iteration:

1. ✅ Vision analyzer detects failures
2. ✅ Checklist identifies what's missing
3. ✅ LLM can generate fix prompts
4. ✅ Progressive img2img workflow proven to work
5. ✅ Re-analysis after each iteration

### Implementation Plan

**Phase 1: Basic Iteration Loop**
1. Detect failure (score < 7 OR checklist < 85%)
2. Generate fix prompt from missing checklist items
3. Single img2img pass with denoise 0.8
4. Re-analyze, pass/fail decision

**Phase 2: Progressive Refinement**
1. Break fixes into multiple steps
2. Major changes first (high denoise)
3. Refinements second (low denoise)
4. Iterate until pass or max attempts

**Phase 3: Advanced Techniques** (Future)
1. Inpainting for hands/faces
2. Seed variation (try multiple times, pick best)
3. CFG scheduling
4. Upscaling workflow

---

## Research Sources

### Professional Workflows
- [Stable Diffusion Img2Img Guide 2025](https://www.aiarty.com/stable-diffusion-guide/stable-diffusion-img2img.htm)
- [Image to Image Complete Technical Guide](https://www.cursor-ide.com/blog/image-to-image-stable-diffusion-complete-guide)
- [Stable Diffusion Workflow](https://stable-diffusion-art.com/workflow/)
- [Master Stable Diffusion Img2Img with Shakker AI](https://wiki.shakker.ai/en/stable-diffusion-img2img)
- [How to Use img2img in Stable Diffusion](https://stable-diffusion-art.com/img2img/)

### OpenArt AI
- [OpenArt AI Review 2025](https://skywork.ai/blog/openart-ai-review-2025-features-pricing-pros-cons-alternatives/)
- [AI Art Generator - OpenArt](https://openart.ai/)
- [OpenArt Ultimate Guide](https://copyright-certificate.byu.edu/news/openart-ai-your-ultimate-guide)

### ControlNet
- [ControlNet: A Complete Guide](https://stable-diffusion-art.com/controlnet/)
- [How to use ControlNet with SDXL](https://stable-diffusion-art.com/controlnet-sdxl/)
- [ControlNet ComfyUI Workflows](https://stable-diffusion-art.com/controlnet-comfyui/)
- [Mastering Pose Changes: Stable Diffusion & ControlNet](https://www.nextdiffusion.ai/tutorials/mastering-pose-changes-stable-diffusion-controlnet)
- [The Ultimate Guide to ControlNet](https://education.civitai.com/civitai-guide-to-controlnet/)

---

## Conclusion

**We're on the right path.** ✅

Our progressive img2img approach matches professional workflows. The only difference is:
- Pros have nice UIs and pre-built workflows
- We're building the automation from scratch

**What we learned:**
1. Professional tools use the same techniques we're using
2. Progressive iteration with appropriate denoise levels is the standard
3. ControlNet is for pose *transfer*, not pose *creation*
4. Inpainting and seed variation are enhancements, not requirements

**Next step:** Build the automated iteration loop using the progressive approach we just proved works.

---

**Status:** Ready to implement Phase 1 of automated iteration system.
