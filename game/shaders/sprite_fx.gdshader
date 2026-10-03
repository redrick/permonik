shader_type canvas_item;

uniform float flash : hint_range(0.0, 1.0) = 0.0;
uniform vec4 flash_color : source_color = vec4(1.0, 0.95, 0.85, 1.0);
uniform float outline : hint_range(0.0, 4.0) = 0.0;
uniform vec4 outline_color : source_color = vec4(0.9, 0.2, 0.15, 1.0);
uniform float dissolve : hint_range(0.0, 1.0) = 0.0;
uniform vec4 tint : source_color = vec4(1.0, 1.0, 1.0, 1.0);
uniform float stone : hint_range(0.0, 1.0) = 0.0;

varying vec4 vcol;

void vertex() {
	vcol = COLOR;
}

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453);
}

void fragment() {
	vec4 c = texture(TEXTURE, UV);
	if (outline > 0.0 && c.a < 0.5) {
		vec2 px = TEXTURE_PIXEL_SIZE * outline;
		float a = texture(TEXTURE, UV + vec2(px.x, 0.0)).a + texture(TEXTURE, UV - vec2(px.x, 0.0)).a
			+ texture(TEXTURE, UV + vec2(0.0, px.y)).a + texture(TEXTURE, UV - vec2(0.0, px.y)).a;
		if (a > 0.5) {
			c = outline_color;
		}
	}
	c.rgb *= tint.rgb;
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
