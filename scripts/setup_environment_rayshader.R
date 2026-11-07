# Install optional rayshader dependencies into this project's isolated library.
# Run with a current official CRAN Rscript; no system/user package libraries are changed.
script <- grep("^--file=", commandArgs(), value=TRUE)
project <- dirname(dirname(normalizePath(sub("^--file=", "", script[[1]]), winslash="/")))
root <- file.path(project, "work", "rayshader")
lib <- file.path(root, "library")
dir.create(lib, recursive=TRUE, showWarnings=FALSE)
.libPaths(c(lib, .Library), include.site=FALSE)
options(repos=c(CRAN="https://cloud.r-project.org"), timeout=180)
install.packages(c("rayshader", "jsonlite", "png"), lib=lib,
                 type=if (.Platform$OS.type=="windows") "binary" else "source", dependencies=NA)
writeLines(capture.output(sessionInfo()), file.path(root,"sessionInfo.txt"))
write.csv(installed.packages(lib.loc=lib)[,c("Package","Version")],
          file.path(root,"package-versions.csv"), row.names=FALSE)
for (pkg in c("rayshader","jsonlite","png")) stopifnot(requireNamespace(pkg, quietly=TRUE))
cat("PROJECT_LOCAL_RAYSHADER_READY\n")
