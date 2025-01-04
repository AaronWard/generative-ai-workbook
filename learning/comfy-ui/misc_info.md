

### V1.5 SD MODEL - TRAINED ON 512X512PX IMAGES SO YOU CAN DO CLOSE TO THOSE VALUES

For v1.5 models, the recommended image sizes to maintain quality and avoid distortions are:

512x512 px: This is the native resolution and the most stable size.
512x768 px: A slightly taller aspect ratio that can be used without significant distortions.
768x512 px: A slightly wider aspect ratio that also works well.

But you can use other values between 512 and 768, preferable divisible by 64.
Using sizes significantly larger than these, like 1024x1024 px or beyond, might lead to issues where the model generates artifacts or duplicates, such as double heads, due to its training on 512x512 px images.

Examples of resolutions:
512x768px: OK
512x704px: OK
512x640px: OK
512x576px: OK
768x512px: OK
704x512px: OK
640x512px: OK
576x512px: OK
1024x1024px: NOT OK

