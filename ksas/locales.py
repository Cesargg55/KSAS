"""
KSAS Localization File
Contains translations for English (EN) and Spanish (ES).
"""

TRANSLATIONS = {
    'EN': {
        # Main Window
        'app_title': "KSAS - Kaesar Star Analysis System v4.1",
        'main_title': "🔬 KSAS - Autonomous Exoplanet Hunter 🔬",
        'current_target': "Current Target",
        'statistics': "Statistics",
        'session_analyzed': "📊 Session Analyzed",
        'total_analyzed': "🏆 Total (Historical)",
        'skipped': "⏭️ Skipped",
        'candidates': "🌟 Candidates",
        'rejected': "❌ Rejected",
        'analysis_status': "Analysis Status",
        'latest_results': "Latest Results",
        'pause': "⏸️ PAUSE",
        'resume': "▶️ RESUME",
        'btn_manager': "📋 Candidate Manager",
        'btn_verifier': "🔍 TIC Verifier",
        'btn_manual': "🔬 Re-analyze TIC",
        'btn_scanner': "📊 Scan Candidates",
        'event_log': "Event Log",
        'lightcurve_preview': "Light Curve Preview",
        'waiting_data': "Waiting for data...",
        'how_it_works': "How it works",
        'found_one': "Found one?",
        
        # Candidate Manager
        'manager_title': "📋 Candidate Manager",
        'refresh': "🔄 Refresh",
        'open_observatory': "🔭 Open Observatory",
        'delete': "🗑️ Delete",
        'export_csv': "💾 Export CSV",
        'col_tic': "TIC ID",
        'col_score': "Score",
        'col_period': "Period (d)",
        'col_depth': "Depth (%)",
        'col_snr': "SNR",
        'col_quality': "Quality",
        'col_disposition': "Disposition",
        'filter': "Filter:",
        'filter_all': "All",
        'filter_excellent': "⭐⭐⭐ Excellent",
        'filter_good': "⭐⭐ Good",
        'filter_fair': "⭐ Fair",
        'status_discovered': "Already Discovered",
        'status_new': "⭐ POTENTIALLY NEW",
        'status_unreviewed': "Unreviewed",
        'select_candidate': "Select a candidate to view details",
        'selected_candidate': "Selected Candidate:",
        'btn_mark_discovered': "✓ Mark as Discovered",
        'btn_mark_new': "★ Mark as NEW",
        'btn_open_report': "📂 Open Report",
        'title_mark_discovered': "Mark as Discovered",
        'title_mark_new': "Mark as Potentially NEW",
        'notes_optional': "Notes (optional):",
        'notes_new': "Notes (verification steps, observations, etc.):",
        'save': "Save",
        'success': "Success",
        'marked_discovered': "marked as discovered.",
        'marked_new': "marked as potentially NEW!",
        'no_selection': "No Selection",
        'select_first': "Please select a candidate first.",
        'file_not_found': "File Not Found",
        'report_not_found': "Report not found:",
        
        # Observatory
        'observatory_title': "🔭 The Observatory",
        'physical_props': "🪐 Physical Properties",
        'intelligent_analysis': "🧠 Intelligent Analysis",
        'vetting_status': "🛡️ Vetting Status",
        'calculating': "Calculating...",
        'checking': "Checking...",
        'passed_tests': "✅ PASSED all tests",
        'failed_tests': "❌ FAILED vetting checks",
        'graph_phase': "Phase Folded Lightcurve",
        'graph_full': "Full Lightcurve",
        'loading_data': "Loading Data...",
        'btn_graph_guide': "❓ What are these graphs?",
        'guide_title': "Graph Guide - What are we seeing?",
        'got_it': "Got it!",
        'target_label': "TARGET:",
        'score_label': "SCORE:",
        'radius': "Radius:",
        'orbit': "Orbit:",
        'temp': "Temp:",
        'type': "Type:",
        
        # Migration
        'migration_title': "Database Update Required",
        'migration_prompt': "Old candidate database format detected.\n\nTo continue, data must be updated (calculating scores and quality).\n\nDo you want to update now? (If No, the program will exit)",
        'migration_success': "Database updated successfully.",
        'migration_cancel': "Update canceled. Exiting program.",
        
        # Report Generation
        'reports_missing_title': "Missing Reports",
        'reports_missing_prompt': "{count} candidates found without report images.\n\nDo you want to generate them now?\n(This will download data and may take a few minutes)",
        'generating_reports': "Generating missing reports...",
        'report_generated': "Generated: {tic}",
        'report_generation_complete': "Report generation complete.",
        'report_generation_skipped': "Report generation skipped.",
        
        # Manual Analyzer
        'manual_title': "🔬 Manual TIC Analyzer",
        'enter_tic': "Enter TIC ID:",
        'analyze_btn': "🚀 ANALYZE",
        'analyzing': "Analyzing...",
        'ready': "Ready",
        
        # Common
        'error': "Error",
        'warning': "Warning",
        'confirm': "Confirm",
        'yes': "Yes",
        'no': "No",
        'ok': "OK",
        'cancel': "Cancel"
    },
    
    'ES': {
        # Main Window
        'app_title': "KSAS - Sistema de Análisis Estelar Kaesar v4.1",
        'main_title': "🔬 KSAS - Cazador Autónomo de Exoplanetas 🔬",
        'current_target': "Objetivo Actual",
        'statistics': "Estadísticas",
        'session_analyzed': "📊 Sesión Analizada",
        'total_analyzed': "🏆 Total (Histórico)",
        'skipped': "⏭️ Omitidos",
        'candidates': "🌟 Candidatos",
        'rejected': "❌ Rechazados",
        'analysis_status': "Estado del Análisis",
        'latest_results': "Últimos Resultados",
        'pause': "⏸️ PAUSAR",
        'resume': "▶️ REANUDAR",
        'btn_manager': "📋 Gestor de Candidatos",
        'btn_verifier': "🔍 Verificador TIC",
        'btn_manual': "🔬 Re-analizar TIC",
        'btn_scanner': "📊 Escanear Candidatos",
        'event_log': "Registro de Eventos",
        'lightcurve_preview': "Vista Previa Curva de Luz",
        'waiting_data': "Esperando datos...",
        'how_it_works': "Cómo funciona",
        'found_one': "¿Encontraste uno?",
        
        # Candidate Manager
        'manager_title': "📋 Gestor de Candidatos",
        'refresh': "🔄 Actualizar",
        'open_observatory': "🔭 Abrir Observatorio",
        'delete': "🗑️ Eliminar",
        'export_csv': "💾 Exportar CSV",
        'col_tic': "ID TIC",
        'col_score': "Puntuación",
        'col_period': "Periodo (d)",
        'col_depth': "Profundidad (%)",
        'col_snr': "SNR",
        'col_quality': "Calidad",
        'col_disposition': "Disposición",
        'filter': "Filtrar:",
        'filter_all': "Todos",
        'filter_excellent': "⭐⭐⭐ Excelente",
        'filter_good': "⭐⭐ Bueno",
        'filter_fair': "⭐ Regular",
        'status_discovered': "Ya Descubierto",
        'status_new': "⭐ POTENCIALMENTE NUEVO",
        'status_unreviewed': "Sin Revisar",
        'select_candidate': "Selecciona un candidato para ver detalles",
        'selected_candidate': "Candidato Seleccionado:",
        'btn_mark_discovered': "✓ Marcar como Descubierto",
        'btn_mark_new': "★ Marcar como NUEVO",
        'btn_open_report': "📂 Abrir Informe",
        'title_mark_discovered': "Marcar como Descubierto",
        'title_mark_new': "Marcar como Potencialmente NUEVO",
        'notes_optional': "Notas (opcional):",
        'notes_new': "Notas (pasos de verificación, observaciones, etc.):",
        'save': "Guardar",
        'success': "Éxito",
        'marked_discovered': "marcado como descubierto.",
        'marked_new': "marcado como potencialmente NUEVO!",
        'no_selection': "Sin Selección",
        'select_first': "Por favor selecciona un candidato primero.",
        'file_not_found': "Archivo No Encontrado",
        'report_not_found': "Informe no encontrado:",
        
        # Observatory
        'observatory_title': "🔭 El Observatorio",
        'physical_props': "🪐 Propiedades Físicas",
        'intelligent_analysis': "🧠 Análisis Inteligente",
        'vetting_status': "🛡️ Estado de Validación",
        'calculating': "Calculando...",
        'checking': "Comprobando...",
        'passed_tests': "✅ PASÓ todas las pruebas",
        'failed_tests': "❌ FALLÓ validación",
        'graph_phase': "Curva de Luz (Fase Plegada)",
        'graph_full': "Curva de Luz Completa",
        'loading_data': "Cargando Datos...",
        'btn_graph_guide': "❓ ¿Qué son estas gráficas?",
        'guide_title': "Guía de Gráficas - ¿Qué estamos viendo?",
        'got_it': "¡Entendido!",
        'target_label': "OBJETIVO:",
        'score_label': "PUNTUACIÓN:",
        'radius': "Radio:",
        'orbit': "Órbita:",
        'temp': "Temp:",
        'type': "Tipo:",
        
        # Migration
        'migration_title': "Actualización de Base de Datos Requerida",
        'migration_prompt': "Se ha detectado un formato antiguo en la base de datos de candidatos.\n\nPara continuar, es necesario actualizar los datos (calcular puntuaciones y calidad).\n\n¿Desea actualizar ahora? (Si selecciona No, el programa se cerrará)",
        'migration_success': "Base de datos actualizada correctamente.",
        'migration_cancel': "Actualización cancelada. Cerrando programa.",
        
        # Report Generation
        'reports_missing_title': "Informes Faltantes",
        'reports_missing_prompt': "Se han detectado {count} candidatos sin imagen de informe.\n\n¿Desea generarlas ahora?\n(Esto descargará los datos y puede tardar unos minutos)",
        'generating_reports': "Generando informes faltantes...",
        'report_generated': "Generado: {tic}",
        'report_generation_complete': "Generación de informes completada.",
        'report_generation_skipped': "Generación de informes omitida.",
        
        # Manual Analyzer
        'manual_title': "🔬 Analizador Manual TIC",
        'enter_tic': "Introduce ID TIC:",
        'analyze_btn': "🚀 ANALIZAR",
        'analyzing': "Analizando...",
        'ready': "Listo",
        
        # Common
        'error': "Error",
        'warning': "Advertencia",
        'confirm': "Confirmar",
        'yes': "Sí",
        'no': "No",
        'ok': "Aceptar",
        'cancel': "Cancelar"
    }
}

class Translator:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Translator, cls).__new__(cls)
            cls._instance.language = 'EN' # Default
        return cls._instance
    
    def set_language(self, lang):
        if lang in TRANSLATIONS:
            self.language = lang
            
    def get(self, key):
        """Get translated string."""
        return TRANSLATIONS.get(self.language, TRANSLATIONS['EN']).get(key, key)

# Global instance
T = Translator()
