"""Mouse Clicker page — UI layout only; wired to worker/thread logic separately."""
from __future__ import annotations

from PyQt6.QtCore import Qt, QThread
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QButtonGroup,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.config import ClickerStatus, ClickMode, LimitMode, MouseButtonOption, PositionMode, TimeUnit
from app.core.mouse_clicker import MouseClickerWorker, MouseClickSettings, PointPicker
from app.ui.widgets import PageHeader, StatusIndicator


class MousePage(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._thread: QThread | None = None
        self._worker: MouseClickerWorker | None = None
        self._point_picker = PointPicker()
        self._point_picker.point_picked.connect(self._on_point_picked)
        self._picking_target: str | None = None

        root = QVBoxLayout(self)
        root.setContentsMargins(28, 24, 28, 20)
        root.setSpacing(14)

        root.addWidget(
            PageHeader(
                "Mouse Clicker",
                "Automate clicks at your cursor, a fixed point, or a sequence of points.",
            )
        )

        grid = QGridLayout()
        grid.setHorizontalSpacing(14)
        grid.setVerticalSpacing(14)
        root.addLayout(grid, 1)

        grid.addWidget(self._build_click_settings_group(), 0, 0)
        grid.addWidget(self._build_interval_group(), 1, 0)
        grid.addWidget(self._build_position_group(), 0, 1, 2, 1)
        grid.addWidget(self._build_limit_group(), 2, 0, 1, 2)

        grid.setColumnStretch(0, 1)
        grid.setColumnStretch(1, 1)

        root.addLayout(self._build_control_bar())

        self._wire_logic()

    # ---- groups -----------------------------------------------------

    def _build_click_settings_group(self) -> QGroupBox:
        box = QGroupBox("Click Settings")
        form = QFormLayout(box)
        form.setSpacing(10)

        self.button_combo = QComboBox()
        for opt in MouseButtonOption:
            self.button_combo.addItem(opt.value, opt)

        self.mode_combo = QComboBox()
        for mode in ClickMode:
            self.mode_combo.addItem(mode.value, mode)

        form.addRow("Button:", self.button_combo)
        form.addRow("Click mode:", self.mode_combo)
        return box

    def _build_interval_group(self) -> QGroupBox:
        box = QGroupBox("Interval")
        layout = QVBoxLayout(box)
        layout.setSpacing(10)

        row = QHBoxLayout()
        self.interval_spin = QDoubleSpinBox()
        self.interval_spin.setRange(0.001, 3_600_000)
        self.interval_spin.setDecimals(3)
        self.interval_spin.setValue(100)
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["ms", "s"])
        row.addWidget(QLabel("Every:"))
        row.addWidget(self.interval_spin, 1)
        row.addWidget(self.unit_combo)
        layout.addLayout(row)

        self.random_check = QCheckBox("Randomize delay")
        layout.addWidget(self.random_check)

        random_row = QHBoxLayout()
        self.random_min_spin = QDoubleSpinBox()
        self.random_min_spin.setRange(0, 3_600_000)
        self.random_min_spin.setValue(50)
        self.random_max_spin = QDoubleSpinBox()
        self.random_max_spin.setRange(0, 3_600_000)
        self.random_max_spin.setValue(150)
        random_row.addWidget(QLabel("Min:"))
        random_row.addWidget(self.random_min_spin)
        random_row.addWidget(QLabel("Max:"))
        random_row.addWidget(self.random_max_spin)
        layout.addLayout(random_row)

        self.random_min_spin.setEnabled(False)
        self.random_max_spin.setEnabled(False)
        self.random_check.toggled.connect(self.random_min_spin.setEnabled)
        self.random_check.toggled.connect(self.random_max_spin.setEnabled)

        layout.addStretch(1)
        return box

    def _build_position_group(self) -> QGroupBox:
        box = QGroupBox("Click Position")
        layout = QVBoxLayout(box)
        layout.setSpacing(10)

        self.pos_current_radio = QRadioButton("Current cursor position")
        self.pos_fixed_radio = QRadioButton("Fixed coordinates")
        self.pos_multi_radio = QRadioButton("Multiple points (multi-click)")

        self.position_group = QButtonGroup(box)
        for i, radio in enumerate(
            (self.pos_current_radio, self.pos_fixed_radio, self.pos_multi_radio)
        ):
            self.position_group.addButton(radio, i)
            layout.addWidget(radio)

        self.pos_current_radio.setChecked(True)

        self.position_stack = QStackedWidget()
        self.position_stack.addWidget(QWidget())  # current cursor: nothing to configure
        self.position_stack.addWidget(self._build_fixed_coords_panel())
        self.position_stack.addWidget(self._build_multi_points_panel())
        layout.addWidget(self.position_stack, 1)

        self.position_group.idClicked.connect(self.position_stack.setCurrentIndex)
        return box

    def _build_fixed_coords_panel(self) -> QWidget:
        panel = QWidget()
        form = QFormLayout(panel)
        form.setContentsMargins(20, 4, 0, 0)

        self.x_spin = QSpinBox()
        self.x_spin.setRange(0, 20000)
        self.y_spin = QSpinBox()
        self.y_spin.setRange(0, 20000)

        form.addRow("X:", self.x_spin)
        form.addRow("Y:", self.y_spin)

        self.pick_point_btn = QPushButton("Pick on Screen…")
        form.addRow("", self.pick_point_btn)
        return panel

    def _build_multi_points_panel(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(20, 4, 0, 0)
        layout.setSpacing(8)

        self.points_table = QTableWidget(0, 2)
        self.points_table.setHorizontalHeaderLabels(["X", "Y"])
        self.points_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.points_table.verticalHeader().setVisible(False)
        self.points_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.points_table.setMaximumHeight(140)
        layout.addWidget(self.points_table)

        btn_row = QHBoxLayout()
        self.add_point_btn = QPushButton("Add Point…")
        self.remove_point_btn = QPushButton("Remove Selected")
        self.clear_points_btn = QPushButton("Clear All")
        btn_row.addWidget(self.add_point_btn)
        btn_row.addWidget(self.remove_point_btn)
        btn_row.addWidget(self.clear_points_btn)
        layout.addLayout(btn_row)

        return panel

    def _build_limit_group(self) -> QGroupBox:
        box = QGroupBox("Limit && Options")
        layout = QHBoxLayout(box)
        layout.setSpacing(20)

        limit_col = QVBoxLayout()
        self.limit_infinite_radio = QRadioButton("Infinite")
        self.limit_fixed_radio = QRadioButton("Fixed count")
        self.limit_group = QButtonGroup(box)
        self.limit_group.addButton(self.limit_infinite_radio, 0)
        self.limit_group.addButton(self.limit_fixed_radio, 1)
        self.limit_infinite_radio.setChecked(True)

        fixed_row = QHBoxLayout()
        self.limit_spin = QSpinBox()
        self.limit_spin.setRange(1, 10_000_000)
        self.limit_spin.setValue(100)
        self.limit_spin.setEnabled(False)
        self.limit_fixed_radio.toggled.connect(self.limit_spin.setEnabled)
        fixed_row.addWidget(self.limit_fixed_radio)
        fixed_row.addWidget(self.limit_spin)

        limit_col.addWidget(self.limit_infinite_radio)
        limit_col.addLayout(fixed_row)
        limit_col.addStretch(1)

        options_col = QVBoxLayout()
        self.return_cursor_check = QCheckBox("Return cursor to original position after click")
        options_col.addWidget(self.return_cursor_check)
        options_col.addStretch(1)

        layout.addLayout(limit_col, 1)
        layout.addLayout(options_col, 1)
        return box

    def _build_control_bar(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        self.start_btn = QPushButton("Start")
        self.start_btn.setObjectName("PrimaryButton")
        self.start_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_btn.setMinimumWidth(120)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setObjectName("DangerButton")
        self.stop_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop_btn.setMinimumWidth(120)
        self.stop_btn.setEnabled(False)

        self.status_indicator = StatusIndicator()
        self.count_label = QLabel("Clicks: 0")
        self.count_label.setStyleSheet("color: #9099a8;")

        bar.addWidget(self.start_btn)
        bar.addWidget(self.stop_btn)
        bar.addSpacing(12)
        bar.addWidget(self.status_indicator)
        bar.addStretch(1)
        bar.addWidget(self.count_label)
        return bar

    # ---- wiring -------------------------------------------------------

    def _wire_logic(self) -> None:
        self.pick_point_btn.clicked.connect(lambda: self._start_picking("fixed"))
        self.add_point_btn.clicked.connect(lambda: self._start_picking("multi"))
        self.remove_point_btn.clicked.connect(self._remove_selected_points)
        self.clear_points_btn.clicked.connect(self.points_table.clearContents)
        self.clear_points_btn.clicked.connect(lambda: self.points_table.setRowCount(0))

        self.start_btn.clicked.connect(self.start_clicking)
        self.stop_btn.clicked.connect(self.stop_clicking)

    # ---- point picking --------------------------------------------------

    def _start_picking(self, target: str) -> None:
        self._picking_target = target
        button = self.pick_point_btn if target == "fixed" else self.add_point_btn
        button.setEnabled(False)
        button.setText("Click anywhere on screen…")
        self._point_picker.start()

    def _on_point_picked(self, x: int, y: int) -> None:
        if self._picking_target == "fixed":
            self.x_spin.setValue(x)
            self.y_spin.setValue(y)
            self.pick_point_btn.setEnabled(True)
            self.pick_point_btn.setText("Pick on Screen…")
        elif self._picking_target == "multi":
            row = self.points_table.rowCount()
            self.points_table.insertRow(row)
            self.points_table.setItem(row, 0, QTableWidgetItem(str(x)))
            self.points_table.setItem(row, 1, QTableWidgetItem(str(y)))
            self.add_point_btn.setEnabled(True)
            self.add_point_btn.setText("Add Point…")
        self._picking_target = None

    def _remove_selected_points(self) -> None:
        for row in sorted({idx.row() for idx in self.points_table.selectedIndexes()}, reverse=True):
            self.points_table.removeRow(row)

    # ---- clicker lifecycle ---------------------------------------------

    def is_running(self) -> bool:
        return self._thread is not None and self._thread.isRunning()

    def _collect_settings(self) -> MouseClickSettings | None:
        points: list[tuple[int, int]] = []
        for row in range(self.points_table.rowCount()):
            x_item = self.points_table.item(row, 0)
            y_item = self.points_table.item(row, 1)
            try:
                points.append((int(x_item.text()), int(y_item.text())))
            except (AttributeError, ValueError):
                continue

        position_mode = PositionMode.CURRENT
        if self.pos_fixed_radio.isChecked():
            position_mode = PositionMode.FIXED
        elif self.pos_multi_radio.isChecked():
            position_mode = PositionMode.MULTI

        if position_mode is PositionMode.MULTI and not points:
            QMessageBox.warning(
                self,
                "No points added",
                "Add at least one point to the list, or choose a different click position mode.",
            )
            return None

        return MouseClickSettings(
            button=self.button_combo.currentData(),
            click_mode=self.mode_combo.currentData(),
            interval_value=self.interval_spin.value(),
            interval_unit=TimeUnit.MS if self.unit_combo.currentText() == "ms" else TimeUnit.SEC,
            randomize=self.random_check.isChecked(),
            random_min=self.random_min_spin.value(),
            random_max=self.random_max_spin.value(),
            position_mode=position_mode,
            fixed_point=(self.x_spin.value(), self.y_spin.value()),
            points=points,
            limit_mode=LimitMode.FIXED if self.limit_fixed_radio.isChecked() else LimitMode.INFINITE,
            limit_count=self.limit_spin.value(),
            return_cursor=self.return_cursor_check.isChecked(),
        )

    def start_clicking(self) -> None:
        if self.is_running():
            return
        settings = self._collect_settings()
        if settings is None:
            return

        self._worker = MouseClickerWorker(settings)
        self._thread = QThread(self)
        self._worker.moveToThread(self._thread)

        self._thread.started.connect(self._worker.run)
        self._worker.status_changed.connect(self.status_indicator.set_status)
        self._worker.count_changed.connect(lambda n: self.count_label.setText(f"Clicks: {n}"))
        self._worker.error.connect(self._on_error)
        self._worker.finished.connect(self._on_finished)
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)

        self._thread.start()
        self._set_inputs_enabled(False)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)

    def stop_clicking(self) -> None:
        if self._worker is not None:
            self._worker.request_stop()
        self.stop_btn.setEnabled(False)

    def toggle_pause(self) -> None:
        if self._worker is not None and self.is_running():
            self._worker.toggle_pause()

    def _on_finished(self) -> None:
        self._worker = None
        self._thread = None
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self._set_inputs_enabled(True)

    def _on_error(self, message: str) -> None:
        QMessageBox.critical(self, "Mouse Clicker error", message)

    def _set_inputs_enabled(self, enabled: bool) -> None:
        for widget in (
            self.button_combo,
            self.mode_combo,
            self.interval_spin,
            self.unit_combo,
            self.random_check,
            self.random_min_spin,
            self.random_max_spin,
            self.pos_current_radio,
            self.pos_fixed_radio,
            self.pos_multi_radio,
            self.x_spin,
            self.y_spin,
            self.pick_point_btn,
            self.points_table,
            self.add_point_btn,
            self.remove_point_btn,
            self.clear_points_btn,
            self.limit_infinite_radio,
            self.limit_fixed_radio,
            self.limit_spin,
            self.return_cursor_check,
        ):
            widget.setEnabled(enabled)
        if enabled:
            # restore dependent-field enabled state instead of blanket enabling
            self.random_min_spin.setEnabled(self.random_check.isChecked())
            self.random_max_spin.setEnabled(self.random_check.isChecked())
            self.limit_spin.setEnabled(self.limit_fixed_radio.isChecked())
