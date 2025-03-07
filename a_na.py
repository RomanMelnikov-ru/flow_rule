import numpy as np
import plotly.graph_objects as go
import streamlit as st


# Функция для вычисления q (девиаторное напряжение) для поверхности текучести
def yield_surface(p, c, phi):
    return p * np.sin(phi) + c * np.cos(phi)


# Функция для вычисления q (девиаторное напряжение) для потенциала пластического течения
def plastic_potential(p, c, psi):
    return p * np.sin(psi) + c * np.cos(psi)


# Основная функция для Streamlit
def main():
    st.title("Визуализация ассоциированного и неассоциированного закона пластического течения")

    # Начальные параметры материала
    c = 10  # Сцепление (кПа)
    phi_initial = 30  # Начальный угол внутреннего трения (градусы)
    psi_initial = 0  # Начальный угол дилатансии (градусы)

    # Слайдеры для углов
    phi = st.slider("Угол внутреннего трения ($\\phi$)", 10, 40, phi_initial, step=2)
    nonassociative = st.checkbox("Неассоциированный закон", key="nonassociative_checkbox")
    psi = st.slider("Угол дилатансии ($\\psi$)", -4, 10, psi_initial, step=1, disabled=not nonassociative)

    # Преобразуем углы в радианы
    phi_rad = np.deg2rad(phi)
    psi_rad = np.deg2rad(psi)

    # Диапазон значений p (среднее напряжение)
    p_values = np.linspace(0, 100, 500)

    # Выберем точку на поверхности текучести (например, p = 50 кПа)
    p_point = 50

    # Вычисляем q для поверхности текучести и потенциала
    q_yield = yield_surface(p_values, c, phi_rad)
    q_point = yield_surface(p_point, c, phi_rad)
    q_potential = plastic_potential(p_values, c, psi_rad)

    # Сдвигаем потенциал пластического течения, чтобы он проходил через точку (p_point, q_point)
    q_potential_shifted = q_potential + (q_point - plastic_potential(p_point, c, psi_rad))

    # Создаем график с помощью Plotly
    fig = go.Figure()

    # Поверхность текучести (закрашенная область)
    fig.add_trace(go.Scatter(
        x=p_values, y=q_yield,
        fill='tozeroy',  # Закрашиваем область под кривой
        mode='lines',
        name=fr'Поверхность текучести (φ = {phi}°)',
        line=dict(color='blue'),
        fillcolor='rgba(135, 206, 250, 0.7)',  # Цвет и прозрачность заливки (RGB с альфа-каналом)
    ))

    # Потенциал пластического течения (если неассоциативный закон включен)
    if nonassociative:
        fig.add_trace(go.Scatter(
            x=p_values, y=q_potential_shifted,
            mode='lines',
            name = f'Потенциал пластического течения (ψ = {psi}°)',
            line=dict(color='orange', dash='dash'),
        ))

    # Точка на поверхности текучести
    fig.add_trace(go.Scatter(
        x=[p_point], y=[q_point],
        mode='markers',
        name='Точка напряженного состояния на поверхности текучести',
        marker=dict(color='red', size=12),
    ))

    # Векторы и их составляющие
    vector_length = 40  # Длина векторов

    # Ассоциативный закон
    dx_yield = -vector_length
    dy_yield = -vector_length * (-1 / np.tan(phi_rad))
    length_yield = np.sqrt(dx_yield ** 2 + dy_yield ** 2)
    dx_yield_normalized = dx_yield / length_yield * vector_length
    dy_yield_normalized = dy_yield / length_yield * vector_length

    # Добавляем стрелку для ассоциативного закона
    fig.add_annotation(
        x=p_point + dx_yield_normalized, y=q_point + dy_yield_normalized,
        ax=p_point, ay=q_point,
        xref="x", yref="y",
        axref="x", ayref="y",
        text="",  # Текст не нужен
        showarrow=True,
        arrowhead=2,
        arrowsize=1,
        arrowwidth=2,
        arrowcolor="blue",
    )

    # Разложение вектора на горизонтальную и вертикальную составляющие
    fig.add_trace(go.Scatter(
        x=[p_point, p_point + dx_yield_normalized], y=[q_point, q_point],
        mode='lines',
        name='Горизонтальная составляющая (ассоциированный закон)',
        line=dict(color='blue', dash='dot', width=1),
    ))
    fig.add_trace(go.Scatter(
        x=[p_point + dx_yield_normalized, p_point + dx_yield_normalized], y=[q_point, q_point + dy_yield_normalized],
        mode='lines',
        name='Вертикальная составляющая (ассоциированный закон)',
        line=dict(color='blue', dash='dot', width=1),
    ))

    # Неассоциативный закон (если включен)
    if nonassociative:
        if psi == 0:
            # Если угол дилатансии равен 0, вектор направлен вертикально вверх
            dx_potential = 0
            dy_potential = vector_length
        else:
            # Иначе вычисляем нормаль к потенциалу
            dx_potential = -vector_length
            dy_potential = -vector_length * (-1 / np.tan(psi_rad))
            # Убедимся, что вертикальная составляющая всегда положительная
            if dy_potential < 0:
                dx_potential *= -1
                dy_potential *= -1

        length_potential = np.sqrt(dx_potential ** 2 + dy_potential ** 2)
        dx_potential_normalized = dx_potential / length_potential * vector_length
        dy_potential_normalized = dy_potential / length_potential * vector_length

        # Добавляем стрелку для неассоциативного закона
        fig.add_annotation(
            x=p_point + dx_potential_normalized, y=q_point + dy_potential_normalized,
            ax=p_point, ay=q_point,
            xref="x", yref="y",
            axref="x", ayref="y",
            text="",  # Текст не нужен
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="orange",
        )

        # Разложение вектора на горизонтальную и вертикальную составляющие
        fig.add_trace(go.Scatter(
            x=[p_point, p_point + dx_potential_normalized], y=[q_point, q_point],
            mode='lines',
            name='Горизонтальная составляющая (неассоциированный закон)',
            line=dict(color='orange', dash='dot', width=1),
        ))
        fig.add_trace(go.Scatter(
            x=[p_point + dx_potential_normalized, p_point + dx_potential_normalized],
            y=[q_point, q_point + dy_potential_normalized],
            mode='lines',
            name='Вертикальная составляющая (неассоциированный закон)',
            line=dict(color='orange', dash='dot', width=1),
        ))

    # Настройка графика
    fig.update_layout(
        title="Поверхность текучести и потенциал пластического течения в плоскости q-p",
        xaxis_title="Объемная деформация (ε<sub>v</sub>)",
        yaxis_title="Деформация сдвига γ",
        legend_title="Легенда",
        showlegend=True,
        xaxis_range=[0, 100],
        yaxis_range=[0, 100],
        template="plotly_white",
    )
    # Убираем значения осей
    fig.update_xaxes(tickvals=[], ticktext=[])  # Для оси X
    fig.update_yaxes(tickvals=[], ticktext=[])  # Для оси Y

    # Отображаем график в Streamlit
    st.plotly_chart(fig, use_container_width=True)


# Запуск приложения
if __name__ == "__main__":
    main()
