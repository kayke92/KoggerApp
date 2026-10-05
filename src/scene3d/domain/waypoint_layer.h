#pragma once

#include "scene_object.h"

#include <QStringList>

class WaypointLayer : public SceneObject
{
    Q_OBJECT

public:
    class WaypointLayerRenderImplementation : public SceneObject::RenderImplementation
    {
    public:
        void render(QOpenGLFunctions* ctx,
                    const QMatrix4x4& mvp,
                    const QMap<QString, std::shared_ptr<QOpenGLShaderProgram>>& shaderProgramMap) const override;

        QStringList labels_;
        int selectedIndex_ = -1;
    };

    explicit WaypointLayer(QObject* parent = nullptr);

    void appendWaypoint(const QVector3D& position, const QString& label);
    void setSelectedIndex(int index);
    int selectedIndex() const;
    void clearData() override;
};
