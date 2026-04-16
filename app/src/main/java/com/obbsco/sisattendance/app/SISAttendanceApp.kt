package com.obbsco.sisattendance.app

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import com.obbsco.sisattendance.data.AuthRepository
import com.obbsco.sisattendance.data.FaceRepository
import com.obbsco.sisattendance.data.NetworkModule
import com.obbsco.sisattendance.data.SessionManager
import com.obbsco.sisattendance.ui.LoginScreen
import com.obbsco.sisattendance.ui.ScanScreen
import kotlinx.coroutines.launch

private enum class AppScreen {
    SPLASH,
    LOGIN,
    SCAN
}

@Composable
fun SISAttendanceApp() {
    val context = LocalContext.current.applicationContext
    val scope = rememberCoroutineScope()

    val sessionManager = remember { SessionManager(context) }
    val authRepository = remember { AuthRepository(NetworkModule.authApi(sessionManager), sessionManager) }
    val faceRepository = remember { FaceRepository(NetworkModule.faceApi()) }

    var screen by remember { mutableStateOf(AppScreen.SPLASH) }

    LaunchedEffect(Unit) {
        screen = if (authRepository.validateSession()) AppScreen.SCAN else AppScreen.LOGIN
    }

    MaterialTheme {
        Surface(modifier = Modifier.fillMaxSize()) {
            when (screen) {
                AppScreen.SPLASH -> Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }

                AppScreen.LOGIN -> LoginScreen(
                    authRepository = authRepository,
                    onLoggedIn = { screen = AppScreen.SCAN }
                )

                AppScreen.SCAN -> ScanScreen(
                    faceRepository = faceRepository,
                    onLogout = {
                        scope.launch {
                            authRepository.logout()
                            screen = AppScreen.LOGIN
                        }
                    }
                )
            }
        }
    }
}
