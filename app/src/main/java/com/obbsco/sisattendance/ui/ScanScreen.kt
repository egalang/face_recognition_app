package com.obbsco.sisattendance.ui

import android.os.Environment
import android.util.Log
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Matrix
import androidx.exifinterface.media.ExifInterface
import java.io.File
import java.io.FileOutputStream
import android.Manifest
import android.content.pm.PackageManager
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.camera.view.LifecycleCameraController
import androidx.camera.view.PreviewView
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.FilterChip
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.lifecycle.compose.LocalLifecycleOwner
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import com.obbsco.sisattendance.data.AttendanceAction
import com.obbsco.sisattendance.data.FaceRepository
import com.obbsco.sisattendance.data.RecognitionResponse
import kotlinx.coroutines.launch

@Composable
fun ScanScreen(
    faceRepository: FaceRepository,
    onLogout: () -> Unit
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()

    var selectedAction by remember { mutableStateOf(AttendanceAction.SCHOOL_IN) }
    var loading by remember { mutableStateOf(false) }
    var error by remember { mutableStateOf<String?>(null) }
    var result by remember { mutableStateOf<RecognitionResponse?>(null) }
    var lastCaptureAt by remember { mutableLongStateOf(0L) }

    var hasCameraPermission by remember {
        mutableStateOf(
            ContextCompat.checkSelfPermission(
                context,
                Manifest.permission.CAMERA
            ) == PackageManager.PERMISSION_GRANTED
        )
    }

    val permissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { granted ->
        hasCameraPermission = granted
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text("Facial Attendance", style = MaterialTheme.typography.headlineSmall)
            TextButton(onClick = onLogout) {
                Text("Logout")
            }
        }

        Text("Select action")
        ActionSelector(
            selected = selectedAction,
            onSelected = { selectedAction = it }
        )

        if (!hasCameraPermission) {
            Card {
                Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("Camera permission is required.")
                    Button(onClick = {
                        permissionLauncher.launch(Manifest.permission.CAMERA)
                    }) {
                        Text("Grant Camera Permission")
                    }
                }
            }
        } else {
            CameraCaptureView(
                enabled = !loading,
                onImageCaptured = { file ->
                    val now = System.currentTimeMillis()
                    if (now - lastCaptureAt < 2000) {
                        error = "Please wait a moment before scanning again."
                        file.delete()
                        return@CameraCaptureView
                    }

                    scope.launch {
                        loading = true
                        error = null
                        lastCaptureAt = now
                        try {
                            result = faceRepository.recognize(file, selectedAction)
                        } catch (e: Exception) {
                            error = e.message ?: "Recognition failed"
                        } finally {
                            loading = false
                            // file.delete()
                        }
                    }
                },
                onError = { error = it }
            )
        }

        if (loading) {
            LinearProgressIndicator(modifier = Modifier.fillMaxWidth())
        }

        error?.let {
            Card {
                Text(
                    text = it,
                    color = MaterialTheme.colorScheme.error,
                    modifier = Modifier.padding(16.dp)
                )
            }
        }

        result?.let {
            ResultCard(it)
        }
    }
}

@Composable
private fun ActionSelector(
    selected: AttendanceAction,
    onSelected: (AttendanceAction) -> Unit
) {
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            AttendanceAction.values().take(2).forEach { action ->
                FilterChip(
                    selected = selected == action,
                    onClick = { onSelected(action) },
                    label = { Text(action.label) }
                )
            }
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            AttendanceAction.values().drop(2).forEach { action ->
                FilterChip(
                    selected = selected == action,
                    onClick = { onSelected(action) },
                    label = { Text(action.label) }
                )
            }
        }
    }
}

@Composable
private fun CameraCaptureView(
    enabled: Boolean,
    onImageCaptured: (File) -> Unit,
    onError: (String) -> Unit
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val executor = ContextCompat.getMainExecutor(context)

    val controller = remember {
    LifecycleCameraController(context).apply {
        cameraSelector = CameraSelector.DEFAULT_FRONT_CAMERA
        setEnabledUseCases(LifecycleCameraController.IMAGE_CAPTURE)

        // imageCaptureMode = ImageCapture.CAPTURE_MODE_MAXIMIZE_QUALITY
        imageCaptureMode = ImageCapture.CAPTURE_MODE_MINIMIZE_LATENCY
    }
}

    DisposableEffect(lifecycleOwner) {
        controller.bindToLifecycle(lifecycleOwner)
        onDispose { }
    }

    Card {
        Column(
            modifier = Modifier.fillMaxWidth(),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            AndroidView(
                factory = {
                    PreviewView(it).apply {
                        this.controller = controller
                        scaleType = PreviewView.ScaleType.FILL_CENTER
                    }
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(420.dp)
            )

            Button(
                onClick = {
                    val file = File(context.cacheDir, "face_${System.currentTimeMillis()}.jpg")
                    val output = ImageCapture.OutputFileOptions.Builder(file).build()

                    controller.takePicture(
                        output,
                        executor,
                        object : ImageCapture.OnImageSavedCallback {
                            override fun onImageSaved(outputFileResults: ImageCapture.OutputFileResults) {
                                try {
                                    val fixedFile = rotateImageIfRequired(file)
                                    // val fixedFile = processAndOptimizeImage(file)
                                    
                                    // ✅ ADD THIS LINE HERE
                                    Log.d("SCAN_DEBUG", "Captured file: ${fixedFile.absolutePath}, size=${fixedFile.length()}")

                                    onImageCaptured(fixedFile)
                                } catch (e: Exception) {
                                    onError("Image processing failed: ${e.message}")
                                }
                            }

                            override fun onError(exception: ImageCaptureException) {
                                onError(exception.message ?: "Capture failed")
                            }
                        }
                    )
                },
                enabled = enabled,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(12.dp)
            ) {
                if (enabled) {
                    Text("Capture & Scan")
                } else {
                    CircularProgressIndicator(modifier = Modifier.size(20.dp))
                }
            }
        }
    }
}

@Composable
private fun ResultCard(result: RecognitionResponse) {
    val confidence = result.confidence ?: 0.0
    val status = when {
        result.success && result.matched == true && confidence >= 0.90 -> "Matched • Auto accepted"
        result.success && result.matched == true && confidence >= 0.75 -> "Matched • Review suggested"
        result.success && result.matched == true -> "Matched • Low confidence"
        result.success -> "Not matched"
        else -> "Request failed"
    }

    Card {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text("Recognition Result", style = MaterialTheme.typography.titleMedium)
            Text("Status: $status")
            Text("Student: ${result.studentName ?: "-"}")
            Text("Enrollment ID: ${result.enrollmentId ?: "-"}")
            Text("Confidence: ${"%.2f".format(confidence)}")
            Text("Attendance Logged: ${if (result.attendanceLogged == true) "Yes" else "No"}")
            result.message?.let { Text("Message: $it") }
        }
    }
}

fun rotateImageIfRequired(file: File): File {
    val exif = ExifInterface(file.absolutePath)
    val orientation = exif.getAttributeInt(
        ExifInterface.TAG_ORIENTATION,
        ExifInterface.ORIENTATION_NORMAL
    )

    val rotation = when (orientation) {
        ExifInterface.ORIENTATION_ROTATE_90 -> 90f
        ExifInterface.ORIENTATION_ROTATE_180 -> 180f
        ExifInterface.ORIENTATION_ROTATE_270 -> 270f
        else -> 0f
    }

    if (rotation == 0f) return file

    val bitmap = BitmapFactory.decodeFile(file.absolutePath)
    val matrix = Matrix().apply { postRotate(rotation) }

    val rotated = Bitmap.createBitmap(
        bitmap,
        0,
        0,
        bitmap.width,
        bitmap.height,
        matrix,
        true
    )

    val rotatedFile = File(file.parent, "rotated_${file.name}")
    FileOutputStream(rotatedFile).use {
        rotated.compress(Bitmap.CompressFormat.JPEG, 95, it)
    }

    return rotatedFile
}

fun processAndOptimizeImage(file: File): File {
    val exif = ExifInterface(file.absolutePath)
    val orientation = exif.getAttributeInt(
        ExifInterface.TAG_ORIENTATION,
        ExifInterface.ORIENTATION_NORMAL
    )

    val rotation = when (orientation) {
        ExifInterface.ORIENTATION_ROTATE_90 -> 90f
        ExifInterface.ORIENTATION_ROTATE_180 -> 180f
        ExifInterface.ORIENTATION_ROTATE_270 -> 270f
        else -> 0f
    }

    // ✅ Downsample while decoding
    val options = BitmapFactory.Options().apply {
        inJustDecodeBounds = false
        inSampleSize = 2  // 🔥 reduces resolution by ~50%
    }

    var bitmap = BitmapFactory.decodeFile(file.absolutePath, options)

    // ✅ Rotate if needed
    if (rotation != 0f) {
        val matrix = Matrix().apply { postRotate(rotation) }
        bitmap = Bitmap.createBitmap(
            bitmap,
            0,
            0,
            bitmap.width,
            bitmap.height,
            matrix,
            true
        )
    }

    // ✅ Resize to max width (VERY important)
    val maxWidth = 720
    val scale = maxWidth.toFloat() / bitmap.width

    val resized = if (bitmap.width > maxWidth) {
        Bitmap.createScaledBitmap(
            bitmap,
            maxWidth,
            (bitmap.height * scale).toInt(),
            true
        )
    } else {
        bitmap
    }

    val optimizedFile = File(file.parent, "opt_${file.name}")

    FileOutputStream(optimizedFile).use {
        // 🔥 Sweet spot for face recognition
        resized.compress(Bitmap.CompressFormat.JPEG, 70, it)
    }

    return optimizedFile
}