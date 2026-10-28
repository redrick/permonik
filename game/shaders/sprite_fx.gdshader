shader_type canvas_item;

uniform float flash : hint_range(0.0, 1.0) = 0.0;
uniform vec4 flash_color : source_color = vec4(1.0, 0.95, 0.85, 1.0);
uniform float outline : hint_range(0.0, 4.0) = 0.0;
uniform vec4 outline_color : source_color = vec4(0.9, 0.2, 0.15, 1.0);
uniform float dissolve : hint_range(0.0, 1.0) = 0.0;
uniform vec4 tint : source_color = vec4(1.0, 1.0, 1.0, 1.0);
uniform float stone : hint_range(0.0, 1.0) = 0.0;
// Walk foot lock: the legs shear back by `lock` (UV, toward the drawing's back) at the feet, nothing at the hip,
// so the planted foot stays put on the floor while the body travels between two walk frames.
uniform float lock = 0.0;
uniform float leg_h = 0.0;
uniform float ground : hint_range(0.0, 1.0) = 0.0;

varying vec4 vcol;

void vertex() {
	vcol = COLOR;
}

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}

void fragment() {
	vec2 uv = UV;
	float feet = 1.0 - 8.0 * TEXTURE_PIXEL_SIZE.y;
	if (lock != 0.0 && leg_h > 0.0) {
		uv.x += lock * clamp((UV.y - feet + leg_h) / leg_h, 0.0, 1.0);
	}
	vec4 c = texture(TEXTURE, uv);
	if (uv.x < 0.0 || uv.x > 1.0) {
		c = vec4(0.0);
	}
	if (outline > 0.0 && c.a < 0.5) {
		vec2 px = TEXTURE_PIXEL_SIZE * outline;
		float a = texture(TEXTURE, uv + vec2(px.x, 0.0)).a + texture(TEXTURE, uv - vec2(px.x, 0.0)).a
			+ texture(TEXTURE, uv + vec2(0.0, px.y)).a + texture(TEXTURE, uv - vec2(0.0, px.y)).a;
		if (a > 0.5) {
			c = outline_color;
		}
	}
	c.rgb *= tint.rgb;
	if (ground > 0.0) {
		c.rgb *= mix(1.0 - ground, 1.0, smoothstep(0.0, 18.0, (feet - UV.y) / TEXTURE_PIXEL_SIZE.y));
	}
	float g = dot(c.rgb, vec3(0.3, 0.59, 0.11));
	c.rgb = mix(c.rgb, vec3(g * 0.9, g * 0.88, g * 0.85), stone);
	c.rgb = mix(c.rgb, flash_color.rgb, flash * c.a);
	if (dissolve > 0.0) {
		float n = hash(floor(UV / TEXTURE_PIXEL_SIZE / 3.0));
		if (n < dissolve) {
			c.a = 0.0;
		} else if (n < dissolve + 0.06) {
			c.rgb = mix(c.rgb, vec3(0.9, 0.5, 0.2), 0.8);
		}
	}
	c.a *= tint.a;
	COLOR = c * vcol;
}
