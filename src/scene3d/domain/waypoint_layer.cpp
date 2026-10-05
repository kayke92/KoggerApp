#include "waypoint_layer.h"

#include "draw_utils.h"
#include "text_renderer.h"

WaypointLayer::WaypointLayer(QObject* parent)
    : SceneObject(new WaypointLayerRenderImplementation, parent)
{
    setColor(QColor(255, 178, 0));
    setWidth(24.0f);
    setPrimitiveType(GL_POINTS);
}

void WaypointLayer::appendWaypoint(const QVector3D& position, const QString& label)
{
    auto* render = RENDER_IMPL(WaypointLayer);
    render->appendData(position);
    render->labels_.append(label);
    Q_EMIT changed();
    Q_EMIT boundsChanged();
}

void WaypointLayer::setSelectedIndex(int index)
{
    auto* render = RENDER_IMPL(WaypointLayer);
    const int validIndex = (index >= 0 && index < render->data().size()) ? index : -1;
    if (render->selectedIndex_ == validIndex) {
        return;
    }
    render->selectedIndex_ = validIndex;
    Q_EMIT changed();
}

int WaypointLayer::selectedIndex() const
{
    return dynamic_cast<const WaypointLayerRenderImplementation*>(m_renderImpl)->selectedIndex_;
}

void WaypointLayer::clearData()
{
    auto* render = RENDER_IMPL(WaypointLayer);
    render->labels_.clear();
    render->selectedIndex_ = -1;
    SceneObject::clearData();
}

void WaypointLayer::WaypointLayerRenderImplementation::render(
    QOpenGLFunctions* ctx,
    const QMatrix4x4& mvp,
    const QMap<QString, std::shared_ptr<QOpenGLShaderProgram>>& shaderProgramMap) const
{
    if (!m_isVisible || m_data.isEmpty()) {
        return;
    }

    auto shader = shaderProgramMap.value("static", nullptr);
    if (shader && shader->bind()) {
        const int posLoc = shader->attributeLocation("position");
        shader->setUniformValue("matrix", mvp);
        shader->setUniformValue("color", DrawUtils::colorToVector4d(m_color));
        shader->setUniformValue("width", m_width);
        shader->setUniformValue("isPoint", true);
        shader->setUniformValue("isTriangle", false);
        shader->enableAttributeArray(posLoc);
        shader->setAttributeArray(posLoc, m_data.constData());
        ctx->glEnable(34370);
        ctx->glDrawArrays(GL_POINTS, 0, m_data.size());
        ctx->glDisable(34370);
        shader->disableAttributeArray(posLoc);
        shader->setUniformValue("isPoint", false);
        shader->release();
    }

    if (selectedIndex_ >= 0 && selectedIndex_ < m_data.size() && shader && shader->bind()) {
        const int posLoc = shader->attributeLocation("position");
        shader->setUniformValue("matrix", mvp);
        shader->setUniformValue("color", DrawUtils::colorToVector4d(QColor(0, 220, 255)));
        shader->setUniformValue("width", m_width + 14.0f);
        shader->setUniformValue("isPoint", true);
        shader->setUniformValue("isTriangle", false);
        shader->enableAttributeArray(posLoc);
        shader->setAttributeArray(posLoc, &m_data.at(selectedIndex_));
        ctx->glEnable(34370);
        ctx->glDrawArrays(GL_POINTS, 0, 1);
        ctx->glDisable(34370);
        shader->disableAttributeArray(posLoc);
        shader->setUniformValue("isPoint", false);
        shader->release();
    }

    QVector<TextRenderer::Text3DItem> textItems;
    const int count = qMin(m_data.size(), labels_.size());
    textItems.reserve(count);
    for (int i = 0; i < count; ++i) {
        QVector3D textPosition = m_data.at(i) + QVector3D(1.0f, 1.0f, 0.2f);
        textItems.append({QStringView{labels_.at(i)}, 0.045f, textPosition,
                          QVector3D(1.0f, 0.0f, 0.0f)});
    }

    const QColor oldColor = TextRenderer::instance().getColor();
    TextRenderer::instance().setColor(QColor(255, 230, 120));
    TextRenderer::instance().render3DBatch(textItems, ctx, mvp, shaderProgramMap);
    TextRenderer::instance().setColor(oldColor);
}
