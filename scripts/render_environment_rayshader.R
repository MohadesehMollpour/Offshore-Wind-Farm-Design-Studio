# Real rayshader relief texture, isolated from system/user R libraries.
# Rscript --vanilla scripts/render_environment_rayshader.R INPUT.json OUTPUT_DIR [EXAGGERATION]
# OUTPUT terrain-relief.png is RGBA, row 1 north / column 1 west, at input dimensions.
# GeoJSON is retained separately: designation polygons must remain geographic overlays.
args <- commandArgs(trailingOnly = TRUE)
if (length(args) < 2L) stop("Usage: Rscript --vanilla render_environment_rayshader.R input.json output_dir [vertical_exaggeration]")
script_arg <- grep("^--file=", commandArgs(), value = TRUE)
project <- dirname(dirname(normalizePath(sub("^--file=", "", script_arg[[1]]), winslash = "/")))
local_lib <- file.path(project, "work", "rayshader", "library")
.libPaths(c(local_lib, .Library), include.site = FALSE)
options(rgl.useNULL = TRUE)
Sys.setenv(RGL_USE_NULL = "TRUE")
for (pkg in c("jsonlite", "png", "rayshader")) {
  if (!requireNamespace(pkg, quietly = TRUE)) stop("Missing project-local package: ", pkg, "; run scripts/setup_environment_rayshader.R with your chosen Rscript")
}
input <- normalizePath(args[[1]], winslash = "/", mustWork = TRUE)
out <- args[[2]]
dir.create(out, recursive = TRUE, showWarnings = FALSE)
exaggeration <- if (length(args) >= 3L) as.numeric(args[[3]]) else 1
if (length(exaggeration) != 1L || !is.finite(exaggeration) || exaggeration <= 0) stop("Exaggeration must be positive")
payload <- jsonlite::fromJSON(input, simplifyVector = FALSE)
terrain <- payload$terrain
nx <- as.integer(terrain$width); ny <- as.integer(terrain$height)
if (length(nx) != 1L || length(ny) != 1L || nx < 3L || ny < 3L || nx * ny > 4e6) stop("Invalid terrain dimensions")
lon <- as.numeric(unlist(terrain$longitude)); lat <- as.numeric(unlist(terrain$latitude))
if (length(lon) != nx || length(lat) != ny || any(!is.finite(c(lon,lat))) || any(diff(lon) <= 0) || any(diff(lat) >= 0)) stop("Longitude must run west to east and latitude north to south")
rows <- terrain$elevation_m
if (length(rows) != ny || any(lengths(rows) != nx)) stop("Elevation grid does not match width/height")
z <- matrix(vapply(unlist(rows, recursive = FALSE), function(v) if (is.null(v)) NA_real_ else as.numeric(v), numeric(1)), nrow = ny, byrow = TRUE)
z[!is.finite(z)] <- NA_real_
valid <- is.finite(z)
if (!any(valid)) stop("No finite source elevations; terrain rendering aborted")
number <- function(v, fallback) if (is.null(v)) as.numeric(fallback) else as.numeric(v)
dx <- number(terrain$spacing_x_m, terrain$horizontal_spacing_m)
dy <- number(terrain$spacing_y_m, terrain$horizontal_spacing_m)
if (length(dx) != 1L || length(dy) != 1L || any(!is.finite(c(dx,dy))) || min(dx,dy) <= 0) stop("Positive physical grid spacing is required")

# Bilinear interpolation retains NoData: only nonzero-weight finite contributors count.
# Source endpoints remain exact; cells beyond the source footprint are never extrapolated.
linear_sample <- function(v, old, new) {
  indices <- findInterval(new, old, all.inside = TRUE)
  f <- (new - old[indices]) / (old[indices+1L] - old[indices])
  result <- (1-f)*v[indices] + f*v[indices+1L]
  at_left <- abs(f) < 1e-10; at_right <- abs(1-f) < 1e-10
  result[at_left] <- v[indices[at_left]]
  result[at_right] <- v[indices[at_right]+1L]
  result[new < min(old)-1e-7 | new > max(old)+1e-7] <- NA_real_
  result
}
resample <- function(m, oldx, oldy, newx, newy) {
  pass <- t(vapply(seq_len(nrow(m)), function(i) linear_sample(m[i,], oldx, newx), numeric(length(newx))))
  vapply(seq_len(ncol(pass)), function(i) linear_sample(pass[,i], oldy, newy), numeric(length(newy)))
}
x <- (seq_len(nx)-1)*dx; y <- (seq_len(ny)-1)*dy
spacing <- min(dx, dy)
square_x <- seq(0, ceiling(max(x)/spacing)*spacing, by = spacing)
square_y <- seq(0, ceiling(max(y)/spacing)*spacing, by = spacing)
square <- resample(z, x, y, square_x, square_y)
# Rayshader heightmaps are x-major; images produced by height_shade are north-up.
heightmap <- t(square)
zscale <- spacing/exaggeration
shade <- rayshader::sphere_shade(heightmap, texture = "bw", zscale = zscale, progbar = FALSE)
# calculate_normal and height_shade transpose the x-major heightmap into image rows.
# Do not flip y: both arrays already match the source's north-to-south row order.
base <- rayshader::height_shade(heightmap, texture = grDevices::colorRampPalette(c("#183d62", "#377f96", "#90bac0", "#d7ded0"))(256), range = range(z, na.rm = TRUE))
texture <- base
for (channel in 1:3) texture[,,channel] <- base[,,channel] * (0.55 + 0.45*shade[,,1])
rgb <- array(NA_real_, dim = c(ny,nx,3L))
for (channel in 1:3) rgb[,,channel] <- resample(texture[,,channel], square_x, square_y, x, y)
# Normals need adjacent elevations. Mask their NoData halo instead of showing invented relief.
square_valid <- is.finite(square)
normal_valid <- square_valid
for (i in -1:1) for (j in -1:1) {
  r <- pmax(1L,pmin(nrow(square),seq_len(nrow(square))+i))
  c <- pmax(1L,pmin(ncol(square),seq_len(ncol(square))+j))
  normal_valid <- normal_valid & square_valid[r,c,drop=FALSE]
}
alpha <- resample(normal_valid*1, square_x, square_y, x, y)
alpha <- valid & is.finite(alpha) & alpha > 1-1e-8 & apply(is.finite(rgb), c(1,2), all)
rgba <- array(0, dim = c(ny,nx,4L))
for (channel in 1:3) {
  v <- rgb[,,channel]; v[!alpha] <- 0
  v <- pmax(0,pmin(1,v))
  # New rayshader rayimg results use linear-light sRGB, older releases return sRGB arrays.
  if (inherits(base,"rayimg")) v <- ifelse(v <= 0.0031308,12.92*v,1.055*v^(1/2.4)-0.055)
  rgba[,,channel] <- v
}
rgba[,,4] <- alpha*1
png_path <- file.path(out,"terrain-relief.png")
png::writePNG(rgba, png_path)
datum <- if (is.null(terrain$datum)) "not supplied" else as.character(terrain$datum)
# A separate labelled preview keeps cartographic labels out of the Three.js texture.
grDevices::png(file.path(out,"terrain-relief-preview.png"), width=1200, height=1000, type="cairo")
graphics::par(mar=c(3,3,7,3),bg="#edf2f5",fg="#142d43",col.main="#142d43",col.sub="#506578")
graphics::plot.new()
graphics::plot.window(xlim=c(0,max(x)),ylim=c(0,max(y)),asp=1)
graphics::rect(0,0,max(x),max(y),col="#dfe5e9",border=NA)
graphics::rasterImage(grDevices::as.raster(rgba),0,0,max(x),max(y),interpolate=FALSE)
graphics::box(col="#b4c4ce")
graphics::mtext("Seabed relief | rayshader",side=3,line=4.3,cex=1.8,font=2)
graphics::mtext(sprintf("North up | grey = NoData | %s | %.1fx vertical exaggeration",datum,exaggeration),side=3,line=2.5,cex=0.95)
graphics::mtext(sprintf("Elevation %.2f to %.2f m | source %d x %d nodes | transparent NoData retained",min(z,na.rm=TRUE),max(z,na.rm=TRUE),nx,ny),side=3,line=1,cex=0.9)
invisible(grDevices::dev.off())
jsonlite::write_json(payload$geojson, file.path(out,"protected-areas.geojson"), auto_unbox=TRUE, null="null", pretty=FALSE, digits=NA)
meta <- list(renderer = "rayshader::sphere_shade + rayshader::height_shade", r_version = R.version.string,
  rayshader_version = as.character(utils::packageVersion("rayshader")), input = input,
  input_md5 = unname(tools::md5sum(input)), width = nx, height = ny,
  orientation = "north-up; first row north, first column west", texture = "terrain-relief.png",
  longitude = lon, latitude = lat, datum = datum, vertical_exaggeration = exaggeration,
  source_spacing_x_m = dx, source_spacing_y_m = dy, rayshader_square_spacing_m = spacing,
  rayshader_zscale = zscale, source_valid_nodes = sum(valid), source_nodata_nodes = sum(!valid),
  texture_opaque_nodes = sum(alpha), elevation_range_m = unname(range(z,na.rm=TRUE)),
  nodata_policy = "No fill or extrapolation. Bilinear resampling requires finite contributing elevations; transparent alpha masks NoData and adjacent undefined normals.",
  resampling = "bilinear to square physical cells for rayshader, hillshade sampled back to original grid",
  reference_point = payload$reference_point, protected_area_overlay = "separate geographic GeoJSON; no change to source elevations")
jsonlite::write_json(meta, file.path(out,"terrain-relief.metadata.json"), auto_unbox=TRUE, null="null", pretty=TRUE, digits=NA)
cat(jsonlite::toJSON(list(ok=TRUE,texture=normalizePath(png_path,winslash="/"),metadata=file.path(out,"terrain-relief.metadata.json"),width=nx,height=ny,opaque=sum(alpha)), auto_unbox=TRUE),"\n")
