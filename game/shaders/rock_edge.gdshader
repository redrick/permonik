shader_type canvas_item;

// Rock tiles cut along a wobbly line instead of the cell grid. `mask` holds 1 per rock cell (1 texel margin
// of rock around the map), sampled smoothly, so corners round off; noise only ever pushes the line into the
// rock, never over walkable floor. The tops are drawn `height` px above their footprint (3/4 view), so a
// south edge shows the face between the shifted top and the footprint, and the face moves up with the cut.
uniform sampler2D mask : filter_linear, repeat_disable;
uniform sampler2D blur : filter_linear, repeat_disable;
uniform vec2 mask_size;
uniform float cell = 64.0;
uniform float height = 32.0;
uniform float stride = 68.0;
uniform float face_tiles = 3.0;
uniform float depth = 0.3;

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

float m_at(vec2 g) {
	return texture(mask, (g / cell + 1.0) / mask_size).r;
}

// > 0 inside the rock footprint, < 0 outside
float inside(vec2 g) {
	float cut = 0.5 + 0.38 * (0.6 * vnoise(g / 90.0) + 0.25 * vnoise(g / 34.0 + 9.0) + 0.15 * vnoise(g / 13.0 + 17.0));
	return m_at(g) - cut;
}

void fragment() {
	vec2 p = world;
	float t = inside(p + vec2(0.0, height));
	vec4 c = texture(TEXTURE, UV);
	if (t > 0.0) {
		// mirror every other rock top at random so the tile's repeat doesn't read as stripes
		if (hash(floor((p + vec2(0.0, height)) / cell)) > 0.5) {
			float px = UV.x / TEXTURE_PIXEL_SIZE.x;
			float base = floor(px / stride) * stride;
			c = texture(TEXTURE, vec2((base + cell - (px - base)) * TEXTURE_PIXEL_SIZE.x, UV.y));
		}
		float b = texture(blur, (vec2(p.x, p.y + height) / cell + 1.0) / mask_size).r;
		c.rgb *= mix(1.0, 1.0 - depth, smoothstep(0.55, 1.0, b));
		c.rgb *= 0.86 + 0.28 * vnoise(p / 150.0 + 5.0);
		c.rgb *= 1.0 + 0.22 * (1.0 - smoothstep(0.0, 0.12, inside(p + vec2(0.0, height - 7.0)))) * smoothstep(0.03, 0.06, t);
		c.rgb *= mix(0.45, 1.0, smoothstep(0.0, 0.035, t));
	} else {
		float hl = -1.0;
		for (int i = 0; i < 16; i++) {
			float hh = float(i) * height / 16.0;
			if (inside(p + vec2(0.0, hh)) > 0.0) {
				hl = hh;
			}
		}
		if (hl < 0.0) {
			c.a = 0.0;
		} else if (floor(UV.x / TEXTURE_PIXEL_SIZE.x / stride) < face_tiles) {
			float g = p.y + hl + height / 32.0;
			float d = ceil(g / cell) * cell - g;
			c = texture(TEXTURE, UV + vec2(0.0, d * TEXTURE_PIXEL_SIZE.y));
		} else {
			c.rgb *= 0.5;
		}
	}
	COLOR = c;
}
