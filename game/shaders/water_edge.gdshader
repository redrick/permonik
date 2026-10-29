shader_type canvas_item;

// Water drawn along a noisy shoreline instead of the cell grid: `mask` holds 1 per water cell (1 texel margin),
// sampled smoothly; the tiles are also laid on the floor cells around the water so the shore can reach out.
// A dark wet band rims the shore, a pale line marks the waterline, and slow ripples move over the surface.
uniform sampler2D mask : filter_linear, repeat_disable;
uniform vec2 mask_size;
uniform float cell = 64.0;

varying vec2 world;

void vertex() {
	world = (MODEL_MATRIX * vec4(VERTEX, 0.0, 1.0)).xy;
}

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float vnoise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), f.x), mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), f.x), f.y);
}

void fragment() {
	vec2 p = world;
	float m = texture(mask, (p / cell + 1.0) / mask_size).r;
	float t = m - (0.5 + 0.36 * (0.65 * vnoise(p / 80.0 + 3.0) + 0.35 * vnoise(p / 27.0 + 11.0) - 0.5));
	vec4 c = texture(TEXTURE, UV);
	float r = sin(p.x * 0.045 + p.y * 0.02 + TIME * 0.9) * sin(p.y * 0.06 - p.x * 0.015 - TIME * 0.6);
	c.rgb *= 1.0 + 0.1 * r;
	c.rgb = mix(c.rgb, vec3(0.75, 0.82, 0.85), (1.0 - smoothstep(0.0, 0.035, t)) * 0.35);
	float a = smoothstep(-0.01, 0.01, t) * c.a;
	float wet = smoothstep(-0.16, -0.01, t) * (1.0 - step(0.0, t));
	COLOR = vec4(mix(vec3(0.0), c.rgb, step(0.0, t)), max(a, wet * 0.3));
}
